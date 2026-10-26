#!/usr/bin/env python3

import sys
import re
import ipaddress
from lxml import etree

CDATA_FIELDS = {"descr", "detail"}
PORT_PATTERN = re.compile(r"^\d+(?::\d+)?$")

def ip_sort_key(value: str):
    interface = ipaddress.ip_interface(value)
    return (
        interface.version,
        int(interface.ip),
        interface.network.prefixlen,
    )

def port_sort_key(value: str):
    first, _, last = value.partition(":")
    return (
        int(first),
        int(last) if last else int(first),
    )

def sort_pairs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    if not pairs:
        return pairs
    addresses = [address for address, _ in pairs]
    if all(PORT_PATTERN.fullmatch(address) for address in addresses):
        key = lambda pair: port_sort_key(pair[0])
    else:
        try:
            for address in addresses:
                ipaddress.ip_interface(address)
        except ValueError:
            key = lambda pair: pair[0].casefold()
        else:
            key = lambda pair: ip_sort_key(pair[0])
    return sorted(pairs, key=key)

def restore_cdata(alias: etree._Element) -> None:
    for tag in CDATA_FIELDS:
        elem = alias.find(tag)
        if elem is not None and elem.text is not None:
            elem.text = etree.CDATA(elem.text)

def dedupe_pairs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []
    for address, detail in pairs:
        if address in seen:
            continue
        seen.add(address)
        deduped.append((address, detail))
    return deduped

def sort_alias(alias: etree._Element) -> None:
    address_elem = alias.find("address")
    detail_elem = alias.find("detail")
    if address_elem is None or detail_elem is None:
        restore_cdata(alias)
        return
    addresses = (address_elem.text or "").split()
    detail_text = detail_elem.text or ""
    if not addresses and not detail_text:
        details = []
    else:
        details = detail_text.split("||")
    if len(addresses) != len(details):
        name = alias.findtext("name", "<unknown>")
        raise ValueError(
            f"Alias {name!r} has {len(addresses)} address entries "
            f"but {len(details)} detail entries"
        )
    pairs = list(zip(addresses, details))
    pairs = dedupe_pairs(pairs)
    pairs = sort_pairs(pairs)
    if pairs:
        sorted_addresses, sorted_details = zip(*pairs)
        address_elem.text = " ".join(sorted_addresses)
        detail_elem.text = "||".join(sorted_details)
    else:
        address_elem.text = ""
        detail_elem.text = ""
    restore_cdata(alias)

def main() -> None:
    parser = etree.XMLParser(
        strip_cdata=False,
        remove_blank_text=False,
    )
    if len(sys.argv) > 2:
        print(f"Usage: {sys.argv[0]} [filename]", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) == 2:
        source = sys.argv[1]
    elif not sys.stdin.isatty():
        source = sys.stdin.buffer
    else:
        print(
            "supply pfSense Alias XML (or pipe in data) to sort",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        tree = etree.parse(source, parser)
    except (OSError, etree.XMLSyntaxError) as exc:
        print(f"Error reading XML: {exc}", file=sys.stderr)
        sys.exit(1)
    root = tree.getroot()
    try:
        for alias in root.iter("alias"):
            sort_alias(alias)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    tree.write(
        sys.stdout.buffer,
        encoding="utf-8",
        xml_declaration=False,
        pretty_print=True,
    )

if __name__ == "__main__":
    main()
