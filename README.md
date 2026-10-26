# pfSense alias sorter

a Python script for people with both pfSense and OCD (which naturally includes myself)

Will autodetect and sort Aliases by IP/CIDR, numeric port (including ranges e.g. `8000:8010`) or alphabetically.

The program accepts raw XML (piped in) or a filename.

The file can be a complete config.xml or just a fragment containing `<alias></alias>` blocks that you want sorted.

## Examples

test1-unsorted.xml
```
<alias>
	<name>ports_to_block</name>
	<type>port</type>
	<address>21 22 25 137:139 445 1194 1433:1434 3306 3389 5000:5001 23 5060:5080 5900 6789 554 8000 8245 8443 8554 8843 9000 9010 37777:37778</address>
	<descr><![CDATA[ports to block]]></descr>
	<detail><![CDATA[FTP||SSH||SMTP||SMB1||SMB2||OpenVPN||MSSQL||MySQL||RDP||Synology||Telnet||SIP||VNC||Unifi speedtest||NVR - rtsp/stream A||NVR - rtsp/stream B||NVR - ctrl A||HTTP/alt1||NVR - rtsp/stream C||HTTP/alt2||NVR - rtsp/stream D||NVR - rtsp/stream E||NVR - rtsp/stream F]]></detail>
</alias>
```

```
$ pfsense-alias-sort.py test1-unsorted.xml
<alias>
	<name>ports_to_block</name>
	<type>port</type>
	<address>21 22 23 25 137:139 445 554 1194 1433:1434 3306 3389 5000:5001 5060:5080 5900 6789 8000 8245 8443 8554 8843 9000 9010 37777:37778</address>
	<descr><![CDATA[ports to block]]></descr>
	<detail><![CDATA[FTP||SSH||Telnet||SMTP||SMB1||SMB2||NVR - rtsp/stream A||OpenVPN||MSSQL||MySQL||RDP||Synology||SIP||VNC||Unifi speedtest||NVR - rtsp/stream B||NVR - ctrl A||HTTP/alt1||NVR - rtsp/stream C||HTTP/alt2||NVR - rtsp/stream D||NVR - rtsp/stream E||NVR - rtsp/stream F]]></detail>
</alias>
```

```
$ pfsense-alias-sort.py <<EOF
(…paste alias contents…)
EOF
# result will be the same as above
```

related forum thread: https://forum.netgate.com/topic/201586/manually-prune-uninstalled-package-xml-elements-from-config.xml
