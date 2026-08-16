SW402>en
Password:
Password:
SW402#sho run
Building configuration...

Current configuration : 48784 bytes
!
! Last configuration change at 09:12:09 UTC Fri Aug 14 2026 by qytang
!
version 17.8
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
! Call-home is enabled by Smart-Licensing.
service call-home
platform punt-keepalive disable-kernel-core
!
hostname SW402
!
!
vrf definition Mgmt-vrf
 !
 address-family ipv4
 exit-address-family
 !
 address-family ipv6
 exit-address-family
!
vrf definition NJQYT_IT_VN
 !
 address-family ipv4
 exit-address-family
!
no aaa new-model
switch 1 provision c9300-24u
!
!
!
!
ip routing
!
!
!
!
!
ip name-server 10.2.253.11
ip domain lookup source-interface Loopback0
ip domain name qytang.com
ip dhcp relay information option
!
!
!
ip dhcp snooping vlan 10,20
ip dhcp snooping
login on-success log
vtp mode transparent
!
!
!
!
!
!
!
mpls label mode all-vrfs protocol all-afs per-vrf
!
!
flow exporter 10.2.254.11
 destination 10.2.254.11
 transport udp 6007
!
access-session mac-move deny
device-tracking tracking
!
device-tracking policy IPDT_POLICY
 no protocol udp
 tracking enable
!
!
!
crypto pki trustpoint SLA-TrustPoint
 enrollment pkcs12
 revocation-check crl
!
crypto pki trustpoint TP-self-signed-3142001615
 enrollment selfsigned
 subject-name cn=IOS-Self-Signed-Certificate-3142001615
 revocation-check none
 rsakeypair TP-self-signed-3142001615
!
crypto pki trustpoint DNAC-CA
 enrollment mode ra
 enrollment terminal
 usage ssl-client
 revocation-check crl none
 source interface Loopback0
!
crypto pki trustpoint sdn-network-infra-iwan
 enrollment url http://10.2.254.11:80/ejbca/publicweb/apply/scep/sdnscep
 fqdn Switch.qytang.com
 subject-name CN=C9300-24U_FCW2151G0Q2_sdn-network-infra-iwan
 subject-alt-name Switch.qytang.com
 revocation-check crl
 source interface Loopback0
 rsakeypair sdn-network-infra-iwan
 auto-enroll 80 regenerate
!
!
crypto pki certificate chain SLA-TrustPoint
 certificate ca 01
  30820321 30820209 A0030201 02020101 300D0609 2A864886 F70D0101 0B050030
  32310E30 0C060355 040A1305 43697363 6F312030 1E060355 04031317 43697363
  6F204C69 63656E73 696E6720 526F6F74 20434130 1E170D31 33303533 30313934
  3834375A 170D3338 30353330 31393438 34375A30 32310E30 0C060355 040A1305
  43697363 6F312030 1E060355 04031317 43697363 6F204C69 63656E73 696E6720
  526F6F74 20434130 82012230 0D06092A 864886F7 0D010101 05000382 010F0030
  82010A02 82010100 A6BCBD96 131E05F7 145EA72C 2CD686E6 17222EA1 F1EFF64D
  CBB4C798 212AA147 C655D8D7 9471380D 8711441E 1AAF071A 9CAE6388 8A38E520
  1C394D78 462EF239 C659F715 B98C0A59 5BBB5CBD 0CFEBEA3 700A8BF7 D8F256EE
  4AA4E80D DB6FD1C9 60B1FD18 FFC69C96 6FA68957 A2617DE7 104FDC5F EA2956AC
  7390A3EB 2B5436AD C847A2C5 DAB553EB 69A9A535 58E9F3E3 C0BD23CF 58BD7188
  68E69491 20F320E7 948E71D7 AE3BCC84 F10684C7 4BC8E00F 539BA42B 42C68BB7
  C7479096 B4CB2D62 EA2F505D C7B062A4 6811D95B E8250FC4 5D5D5FB8 8F27D191
  C55F0D76 61F9A4CD 3D992327 A8BB03BD 4E6D7069 7CBADF8B DF5F4368 95135E44
  DFC7C6CF 04DD7FD1 02030100 01A34230 40300E06 03551D0F 0101FF04 04030201
  06300F06 03551D13 0101FF04 05300301 01FF301D 0603551D 0E041604 1449DC85
  4B3D31E5 1B3E6A17 606AF333 3D3B4C73 E8300D06 092A8648 86F70D01 010B0500
  03820101 00507F24 D3932A66 86025D9F E838AE5C 6D4DF6B0 49631C78 240DA905
  604EDCDE FF4FED2B 77FC460E CD636FDB DD44681E 3A5673AB 9093D3B1 6C9E3D8B
  D98987BF E40CBD9E 1AECA0C2 2189BB5C 8FA85686 CD98B646 5575B146 8DFC66A8
  467A3DF4 4D565700 6ADF0F0D CF835015 3C04FF7C 21E878AC 11BA9CD2 55A9232C
  7CA7B7E6 C1AF74F6 152E99B7 B1FCF9BB E973DE7F 5BDDEB86 C71E3B49 1765308B
  5FB0DA06 B92AFE7F 494E8A9E 07B85737 F3A58BE1 1A48A229 C37C1E69 39F08678
  80DDCD16 D6BACECA EEBC7CF9 8428787B 35202CDC 60E4616A B623CDBD 230E3AFB
  418616A9 4093E049 4D10AB75 27E86F73 932E35B5 8862FDAE 0275156F 719BB2F0
  D697DF7F 28
        quit
crypto pki certificate chain TP-self-signed-3142001615
 certificate self-signed 01
  30820330 30820218 A0030201 02020101 300D0609 2A864886 F70D0101 05050030
  31312F30 2D060355 04031326 494F532D 53656C66 2D536967 6E65642D 43657274
  69666963 6174652D 33313432 30303136 3135301E 170D3236 30383133 30393435
  34335A17 0D333630 38313230 39343534 335A3031 312F302D 06035504 03132649
  4F532D53 656C662D 5369676E 65642D43 65727469 66696361 74652D33 31343230
  30313631 35308201 22300D06 092A8648 86F70D01 01010500 0382010F 00308201
  0A028201 0100B1EA FE630AB0 D571D70E 0823AAE5 8A6A564F 937D9A85 A42FBA3F
  2DDF0597 4A65A6C4 3F42D26E 0065CB66 F68911B3 E7B311F4 EFAA07F9 2EA9B58E
  5915F88F D46AA7AE 98C439EC EE38A778 ACB2CDEF 4D8CF430 AACBFAC4 49F38DF3
  4968404E CFE4496E 3F037D8D AC74A1AE 3B3CEF1E E326A03B 2DD8B7C8 39C9AB68
  67E068A5 9B03310B 2536DDD4 F0AB9860 310E35F0 28FA7696 73F8C4EF 8F4CE7FE
  81C967CD B0249A78 9AB0B4A4 2C1C8B50 3685A0FD 6DC8A1FB BA411EA1 0FAE2DD8
  9E5CCD61 ABBE624E 80C9986A 4FBE41DE B3C480CE 67640ED6 C8D2BF36 DB4C0E9A
  3091AEC6 F8A21A17 5A87C6FE 8DDC7E80 EC3C3617 7C2C703D FC77C70D 96700C77
  F8DB488E 4DF10203 010001A3 53305130 0F060355 1D130101 FF040530 030101FF
  301F0603 551D2304 18301680 14871BA9 E3990C54 C6F6F8D0 F0B255DE 2B22D70F
  FA301D06 03551D0E 04160414 871BA9E3 990C54C6 F6F8D0F0 B255DE2B 22D70FFA
  300D0609 2A864886 F70D0101 05050003 82010100 65AFCCEB E679683C E8C2A38A
  DEDD1B89 BD3D3B2C EC205E04 73AEF836 DD8C817A 4207B927 E37B2FE5 7529145A
  D01C3550 E82EE4AF 383FA912 055E1BFC 5C1C941A 49485A1E 842BE5CE D7791A9C
  FDA9E029 7CA7A8A1 B2559D08 29436201 D50BBF0C 2EC296CA E934EA4F 992FB298
  0368357F A66B8ECA D54E53E5 C3C1D477 03AB3170 34248AAF 5FA6A46F 4BB6F890
  33FBD1F2 C1B99B34 1FDC95F1 C7BCD86C 9E008955 AEFFFAA8 DE251A24 ADE0D11B
  EF817E42 04CAE9DA 0570D371 40D83CFA 2F83F106 B7C81297 84397CF8 6B43AF91
  6CEC1C61 13704B8E 7AC3A121 E77EF353 15683ECB 86EA0FDC 6BCD83E8 7D578131
  A5622768 2B9C49A9 D9C16790 53F23EBB 26F10592
        quit
crypto pki certificate chain DNAC-CA
 certificate ca 3F2A343E086C62299086E98277D81F0F1AB65DFF
  308203A5 3082028D A0030201 0202143F 2A343E08 6C622990 86E98277 D81F0F1A
  B65DFF30 0D06092A 864886F7 0D01010B 05003062 312D302B 06035504 030C2461
  33653730 3138322D 61306535 2D363331 342D6363 65612D62 35353162 35306131
  64663931 16301406 0355040A 0C0D4369 73636F20 53797374 656D7331 19301706
  0355040B 0C104369 73636F20 444E4120 43656E74 6572301E 170D3236 30343132
  30393532 34345A17 0D323930 31303630 39353234 345A3062 312D302B 06035504
  030C2461 33653730 3138322D 61306535 2D363331 342D6363 65612D62 35353162
  35306131 64663931 16301406 0355040A 0C0D4369 73636F20 53797374 656D7331
  19301706 0355040B 0C104369 73636F20 444E4120 43656E74 65723082 0122300D
  06092A86 4886F70D 01010105 00038201 0F003082 010A0282 010100C2 87898047
  48DCC8BD 98E768EC B28C610A 2B0401F7 D934A918 88045794 A8B389E1 2F1F3665
  A74843C8 92BA2569 545DDB5B EFCC51F8 6496A6DB 33074488 024694D0 6130CC1B
  5DA74746 E9BF21EA ECD68658 4E516BFE 44C3E8AF 7D28E377 D37B5F2E CA406D55
  BC54CCE4 C26D90C2 9805F585 3CFC2807 B30A6657 3A9607C9 01B1563F 07B5BD54
  58B14A05 8C396C53 B94AFBA9 0ACC5C2F 24718251 48A852A6 DB5873C1 F5850DF6
  E8517DEE 47D4A5B7 BF23AE75 F5B2301E C610EC1A A4512BD1 93AA7C16 940428DB
  C0D0999A F04AF5BF 388F2949 39E4915D 79602302 A59E8AF0 3CBB46BB 238113B5
  85B388F8 97A6E04E 33BD2D6E A5C18759 36B137AB E1A22083 6F933B02 03010001
  A3533051 301D0603 551D0E04 16041485 B2BD1B41 A3FAF964 445F58E3 33601A65
  53D9FE30 1F060355 1D230418 30168014 85B2BD1B 41A3FAF9 64445F58 E333601A
  6553D9FE 300F0603 551D1301 01FF0405 30030101 FF300D06 092A8648 86F70D01
  010B0500 03820101 0053B628 525AF621 446B630A CBCCF07A B16BAE20 E92AAA5B
  A4B72DFB 88CBB2B4 A44BD68A F7621278 706B5DCD C120E30D 7702DDC9 F0D64C2D
  3E616AEB 2E88626C 76A1C029 81BD5F7E C86FB2A4 D202E9F3 6EBECD24 FB2EB87A
  EBD80036 410EECB3 BE612C9F 79B723B8 9E72B8F8 23DCCBE5 C9A685A3 A10A5B0A
  ABA840E6 8C35EFE3 BE6B358A 23441C80 ACA2BA94 AD5157D7 426ADC26 1E8AC742
  EC48DF24 E1A1B145 6D60DE5F 8E5B13FC 19508072 F5EF3FEF 67A881F6 AB9B4255
  96FA72D2 1BCFFFD0 2B4C6E5C 4F4D9D51 9C500D0E 0915860E D6A4C2AB 6F74B721
  46BBD065 F0AAADA4 317F5481 BFCFB9FF 4200AF1E 105E778E 526AE743 4FE0091E
  BF98EB7F 9F5BD0EB 8C
        quit
crypto pki certificate chain sdn-network-infra-iwan
 certificate 0B871AA71E2986B5
  30820379 30820261 A0030201 0202080B 871AA71E 2986B530 0D06092A 864886F7
  0D01010D 0500301F 311D301B 06035504 030C1473 646E2D6E 6574776F 726B2D69
  6E667261 2D636130 1E170D32 36303831 34303532 3535315A 170D3237 30383134
  30353235 35315A30 59312030 1E06092A 864886F7 0D010902 0C115377 69746368
  2E717974 616E672E 636F6D31 35303306 03550403 0C2C4339 3330302D 3234555F
  46435732 31353147 3051325F 73646E2D 6E657477 6F726B2D 696E6672 612D6977
  616E3082 0122300D 06092A86 4886F70D 01010105 00038201 0F003082 010A0282
  01010081 4BAF40AB C55EFDAB E617BD9D 399D38FF 01A0DE5D B1E03DCD CA4756E0
  E32C0F2A 8D5733AC 11281260 AB62944B 69C16280 EB908393 142D2041 BB06C582
  435A0FF1 A3B461E8 7478FCF5 529586EE 678B82CA C4094893 CE63BC57 3E8BFA8C
  F28AA918 0D7E3D15 62F16243 B3582B0D 2713411A 450F5778 A2922172 ED60F2CF
  AF3A3A9C 8114016E BE92E019 667A0651 B6BF64C4 B635C633 A2BB1001 A7F7853E
  980E84FD E0A9A1F4 D0C56EE0 E348B873 687A2416 915013D8 1F6CF183 EF1A641A
  D60BDEB9 229D8178 F4C416B4 E4AA0B97 ED9A311C 39577032 C4C42F19 3DB63818
  993C5C24 18735D9F 2B4998BB B3E80248 241AD6F9 6C13AAB1 833F88C4 94E7C1C1
  71418302 03010001 A37F307D 300C0603 551D1301 01FF0402 3000301F 0603551D
  23041830 168014F3 D815BC93 BBACD230 82661FC5 764D0EE4 C0654C30 1D060355
  1D250416 30140608 2B060105 05070302 06082B06 01050507 0304301D 0603551D
  0E041604 14CCB67E 1272E634 F1FF718C 9F4A34CB 3BE3F789 79300E06 03551D0F
  0101FF04 04030205 E0300D06 092A8648 86F70D01 010D0500 03820101 008B6048
  7435CE00 B2188E55 E3B862E6 82B62724 5316BA61 33E17010 FEAEFF68 C910AC19
  B420D89F 484036BE AF7B53E6 7D2328AE B4FDB560 4E8DEE0F 66ED552F 702A36F4
  ECDD836F 40BD6038 E9496AA3 FF37A4ED 3866472C 27F2206D F4AB2BBC D0C41EED
  110042A2 29D33A58 BDFFB67A 45332FC3 34EDCE22 9CB1BDA0 E2E885B8 4FF33415
  9F62449B C608195D 44875CFE A5511FB9 653E648F FB9DFAEF 3C9EAC95 D5506630
  76BA41E0 E32E8A4E 2F15FA03 84915550 BCF404A2 C217B6E8 C598B86D DC69AB52
  FC81AA7E 0FE1E590 C4B414D6 D9D6B445 5D4BBC6E 04EE375B 4748784D A097F60E
  89C7FC2C C99C2827 74E2F1E3 6A70A7AB AAE43FF6 CB3CDA91 03527682 EA
        quit
 certificate ca 0D2C599F6B4F3C3B
  30820323 3082020B A0030201 0202080D 2C599F6B 4F3C3B30 0D06092A 864886F7
  0D01010D 0500301F 311D301B 06035504 030C1473 646E2D6E 6574776F 726B2D69
  6E667261 2D636130 1E170D32 36303431 32313634 3432385A 170D3431 30343132
  31363434 32385A30 1F311D30 1B060355 04030C14 73646E2D 6E657477 6F726B2D
  696E6672 612D6361 30820122 300D0609 2A864886 F70D0101 01050003 82010F00
  3082010A 02820101 00DFA802 62BA5139 D4D1E41F 9C596440 861E5A7E 26762783
  05887FE5 A6266FBA F8D17E6D 203A2AC6 2E89C4AC C09320D2 5321ADF3 8F896873
  5B8A1D72 B2622933 8DA1CEBC EB055C22 75F320A0 B689DF92 B4D5707B EE875BC2
  3A1B2319 CBE23264 8DF9E3BA 396519E7 118424E9 43FC7005 6EAE181B E509E0AE
  155D2065 839CED8C BF907B36 098D7852 01056286 79207C09 F0F3D035 9F89B9C9
  94A4B792 77B35C28 382DE32F ABA4D514 60BAD7A3 541B8197 BBA6C8A8 D5D3449A
  E35546B7 B451C0D2 8B2AB5E1 43477F03 34CBE376 FC5D6EDE E20C9A60 F28406A5
  06570104 81EC1EA8 353ECC6F 4C9F7839 BBE535DE 15BC4D1B 71C3A73B F676ABC3
  FF47A7A7 2A05A892 67020301 0001A363 3061300F 0603551D 130101FF 04053003
  0101FF30 1F060355 1D230418 30168014 F3D815BC 93BBACD2 3082661F C5764D0E
  E4C0654C 301D0603 551D0E04 160414F3 D815BC93 BBACD230 82661FC5 764D0EE4
  C0654C30 0E060355 1D0F0101 FF040403 02018630 0D06092A 864886F7 0D01010D
  05000382 0101007B 23A88C34 04AB840F FBBB2B5A E9CF6E2A 3466D68E 0CEE4C64
  13C7E4F3 2316397D E8A7633B 0F533EE5 BAB6AB19 8962AB73 191107F6 0FF41D68
  F095866A A2A448AE EB4B274A B3B5E3DD 070E7BF2 5FFE4C2C FBC542FC E4ABF9D5
  821013CA 300DE191 65DD8389 C6F59515 039B1FC6 5118CC9B 6CA30786 2C35E709
  547ED3D5 51B7D7F6 59B1C00D B0717859 42998C71 8902B9D4 F1E5A428 3CE21FF9
  CD34AD3D 230FBE93 8F02522A D3613A9C 51DDDB72 A4E26408 24265C47 7BC00FFC
  E80AE026 66A2C5C7 FAF255A0 D841F886 FD97ACD1 7817BDA8 24EDC954 1010C506
  6D466022 EE2D14B0 C7DC24B8 E2666845 CD6AEC8B E2FE5560 E41B7D16 6DDD5FCE
  64D5075E 5EE6B6
        quit
!
!
license boot level network-advantage addon dna-advantage
license smart transport off
service-template DEFAULT_LINKSEC_POLICY_MUST_SECURE
 linksec policy must-secure
service-template DEFAULT_LINKSEC_POLICY_SHOULD_SECURE
 linksec policy should-secure
service-template DEFAULT_CRITICAL_VOICE_TEMPLATE
 voice vlan
service-template DEFAULT_CRITICAL_DATA_TEMPLATE
service-template webauth-global-inactive
 inactivity-timer 3600
service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
service-template DefaultCriticalVoice_SRV_TEMPLATE
 voice vlan
service-template DefaultCriticalAccess_SRV_TEMPLATE
 access-group IPV4_CRITICAL_AUTH_ACL
 access-group IPV6_CRITICAL_AUTH_ACL
device classifier
diagnostic bootup level minimal
memory free low-watermark processor 131046
!
!
!
!
spanning-tree mode rapid-pvst
spanning-tree extend system-id
errdisable recovery cause udld
errdisable recovery cause bpduguard
errdisable recovery cause security-violation
errdisable recovery cause channel-misconfig
errdisable recovery cause pagp-flap
errdisable recovery cause dtp-flap
errdisable recovery cause link-flap
errdisable recovery cause sfp-config-mismatch
errdisable recovery cause gbic-invalid
errdisable recovery cause l2ptguard
errdisable recovery cause psecure-violation
errdisable recovery cause port-mode-failure
errdisable recovery cause dhcp-rate-limit
errdisable recovery cause pppoe-ia-rate-limit
errdisable recovery cause mac-limit
errdisable recovery cause storm-control
errdisable recovery cause inline-power
errdisable recovery cause arp-inspection
errdisable recovery cause link-monitor-failure
errdisable recovery cause oam-remote-failure
errdisable recovery cause loopback
errdisable recovery cause psp
errdisable recovery cause mrp-miscabling
errdisable recovery cause loopdetect
!
enable password 7 01021F105A0501
!
username qytang privilege 15 password 7 13140E060A0203
!
redundancy
 mode sso
crypto engine compliance shield disable
!
!
!
!
!
transceiver type all
 monitoring
!
vlan 10
 name NJQYT-IT
!
vlan 20
 name NJQYT-Sales
!
vlan 2046
 name VOICE_VLAN
!
class-map type control subscriber match-all AAA_SVR_DOWN_AUTHD_HOST
 match authorization-status authorized
 match result-type aaa-timeout
!
class-map type control subscriber match-all AAA_SVR_DOWN_UNAUTHD_HOST
 match authorization-status unauthorized
 match result-type aaa-timeout
!
class-map type control subscriber match-all AUTHC_SUCCESS-AUTHZ_FAIL
 match authorization-status unauthorized
 match result-type success
!
class-map type control subscriber match-all DOT1X
 match method dot1x
!
class-map type control subscriber match-all DOT1X_FAILED
 match method dot1x
 match result-type method dot1x authoritative
!
class-map type control subscriber match-all DOT1X_MEDIUM_PRIO
 match authorizing-method-priority gt 20
!
class-map type control subscriber match-all DOT1X_NO_RESP
 match method dot1x
 match result-type method dot1x agent-not-found
!
class-map type control subscriber match-all DOT1X_TIMEOUT
 match method dot1x
 match result-type method dot1x method-timeout
!
class-map type control subscriber match-any IN_CRITICAL_AUTH
 match activated-service-template DefaultCriticalVoice_SRV_TEMPLATE
!
class-map type control subscriber match-any IN_CRITICAL_AUTH_CLOSED_MODE
 match activated-service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
 match activated-service-template DefaultCriticalVoice_SRV_TEMPLATE
!
class-map type control subscriber match-all MAB
 match method mab
!
class-map type control subscriber match-all MAB_FAILED
 match method mab
 match result-type method mab authoritative
!
class-map type control subscriber match-none NOT_IN_CRITICAL_AUTH
 match activated-service-template DefaultCriticalVoice_SRV_TEMPLATE
!
class-map type control subscriber match-none NOT_IN_CRITICAL_AUTH_CLOSED_MODE
 match activated-service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
 match activated-service-template DefaultCriticalVoice_SRV_TEMPLATE
!
!
class-map match-any system-cpp-police-ewlc-control
  description EWLC Control
class-map match-any system-cpp-police-topology-control
  description Topology control
class-map match-any system-cpp-police-sw-forward
  description Sw forwarding, L2 LVX data packets, LOGGING, Transit Traffic
class-map match-any system-cpp-default
  description EWLC Data, Inter FED Traffic
class-map match-any system-cpp-police-sys-data
  description Openflow, Exception, EGR Exception, NFL Sampled Data, RPF Failed
class-map match-any system-cpp-police-punt-webauth
  description Punt Webauth
class-map match-any system-cpp-police-l2lvx-control
  description L2 LVX control packets
class-map match-any system-cpp-police-forus
  description Forus Address resolution and Forus traffic
class-map match-any system-cpp-police-multicast-end-station
  description MCAST END STATION
class-map match-any system-cpp-police-high-rate-app
  description High Rate Applications
class-map match-any system-cpp-police-multicast
  description MCAST Data
class-map match-any system-cpp-police-l2-control
  description L2 control
class-map match-any system-cpp-police-dot1x-auth
  description DOT1X Auth
class-map match-any system-cpp-police-data
  description ICMP redirect, ICMP_GEN and BROADCAST
class-map match-any system-cpp-police-stackwise-virt-control
  description Stackwise Virtual OOB
class-map match-any non-client-nrt-class
class-map match-any system-cpp-police-routing-control
  description Routing control and Low Latency
class-map match-any system-cpp-police-protocol-snooping
  description Protocol snooping
class-map match-any system-cpp-police-dhcp-snooping
  description DHCP snooping
class-map match-any system-cpp-police-ios-routing
  description L2 control, Topology control, Routing control, Low Latency
class-map match-any system-cpp-police-system-critical
  description System Critical and Gold Pkt
class-map match-any system-cpp-police-ios-feature
  description ICMPGEN,BROADCAST,ICMP,L2LVXCntrl,ProtoSnoop,PuntWebauth,MCASTData,Transit,DOT1XAuth,Swfwd,LOGGING,L2LVXData,ForusTraffic,ForusARP,McastEndStn,Openflow,Exception,EGRExcption,NflSampled,RpfFailed
!
!
policy-map type control subscriber PMAP_DefaultWiredDot1xClosedAuth_1X_MAB
 event session-started match-all
  10 class always do-until-failure
   10 authenticate using dot1x retries 2 retry-time 0 priority 10
 event authentication-failure match-first
  5 class DOT1X_FAILED do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  10 class AAA_SVR_DOWN_UNAUTHD_HOST do-until-failure
   10 activate service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
   20 activate service-template DefaultCriticalVoice_SRV_TEMPLATE
   30 authorize
   40 pause reauthentication
  20 class AAA_SVR_DOWN_AUTHD_HOST do-until-failure
   10 pause reauthentication
   20 authorize
  30 class DOT1X_NO_RESP do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  40 class MAB_FAILED do-until-failure
   10 terminate mab
   20 authentication-restart 60
  50 class DOT1X_TIMEOUT do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  60 class always do-until-failure
   10 terminate dot1x
   20 terminate mab
   30 authentication-restart 60
 event aaa-available match-all
  10 class IN_CRITICAL_AUTH_CLOSED_MODE do-until-failure
   10 clear-session
  20 class NOT_IN_CRITICAL_AUTH_CLOSED_MODE do-until-failure
   10 resume reauthentication
 event agent-found match-all
  10 class always do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
 event inactivity-timeout match-all
  10 class always do-until-failure
   10 clear-session
 event authentication-success match-all
 event violation match-all
  10 class always do-until-failure
   10 restrict
 event authorization-failure match-all
  10 class AUTHC_SUCCESS-AUTHZ_FAIL do-until-failure
   10 authentication-restart 60
!
policy-map type control subscriber PMAP_DefaultWiredDot1xClosedAuth_MAB_1X
 event session-started match-all
  10 class always do-until-failure
   10 authenticate using mab priority 20
 event authentication-failure match-first
  5 class DOT1X_FAILED do-until-failure
   10 terminate dot1x
   20 authentication-restart 60
  10 class AAA_SVR_DOWN_UNAUTHD_HOST do-until-failure
   10 activate service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
   20 activate service-template DefaultCriticalVoice_SRV_TEMPLATE
   30 authorize
   40 pause reauthentication
  20 class AAA_SVR_DOWN_AUTHD_HOST do-until-failure
   10 pause reauthentication
   20 authorize
  30 class MAB_FAILED do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
  40 class DOT1X_NO_RESP do-until-failure
   10 terminate dot1x
   20 authentication-restart 60
  50 class DOT1X_TIMEOUT do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  60 class always do-until-failure
   10 terminate mab
   20 terminate dot1x
   30 authentication-restart 60
 event aaa-available match-all
  10 class IN_CRITICAL_AUTH_CLOSED_MODE do-until-failure
   10 clear-session
  20 class NOT_IN_CRITICAL_AUTH_CLOSED_MODE do-until-failure
   10 resume reauthentication
 event agent-found match-all
  10 class always do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
 event inactivity-timeout match-all
  10 class always do-until-failure
   10 clear-session
 event authentication-success match-all
 event violation match-all
  10 class always do-until-failure
   10 restrict
 event authorization-failure match-all
  10 class AUTHC_SUCCESS-AUTHZ_FAIL do-until-failure
   10 authentication-restart 60
!
policy-map type control subscriber PMAP_DefaultWiredDot1xLowImpactAuth_1X_MAB
 event session-started match-all
  10 class always do-until-failure
   10 authenticate using dot1x retries 2 retry-time 0 priority 10
 event authentication-failure match-first
  5 class DOT1X_FAILED do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  10 class AAA_SVR_DOWN_UNAUTHD_HOST do-until-failure
   10 activate service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
   20 activate service-template DefaultCriticalVoice_SRV_TEMPLATE
   25 activate service-template DefaultCriticalAccess_SRV_TEMPLATE
   30 authorize
   40 pause reauthentication
  20 class AAA_SVR_DOWN_AUTHD_HOST do-until-failure
   10 pause reauthentication
   20 authorize
  30 class DOT1X_NO_RESP do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  40 class MAB_FAILED do-until-failure
   10 terminate mab
   20 authentication-restart 60
  50 class DOT1X_TIMEOUT do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  60 class always do-until-failure
   10 terminate dot1x
   20 terminate mab
   30 authentication-restart 60
 event aaa-available match-all
  10 class IN_CRITICAL_AUTH do-until-failure
   10 clear-session
  20 class NOT_IN_CRITICAL_AUTH do-until-failure
   10 resume reauthentication
 event agent-found match-all
  10 class always do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
 event inactivity-timeout match-all
  10 class always do-until-failure
   10 clear-session
 event authentication-success match-all
 event violation match-all
  10 class always do-until-failure
   10 restrict
 event authorization-failure match-all
  10 class AUTHC_SUCCESS-AUTHZ_FAIL do-until-failure
   10 authentication-restart 60
!
policy-map type control subscriber PMAP_DefaultWiredDot1xLowImpactAuth_MAB_1X
 event session-started match-all
  10 class always do-until-failure
   10 authenticate using mab priority 20
 event authentication-failure match-first
  5 class DOT1X_FAILED do-until-failure
   10 terminate dot1x
   20 authentication-restart 60
  10 class AAA_SVR_DOWN_UNAUTHD_HOST do-until-failure
   10 activate service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
   20 activate service-template DefaultCriticalVoice_SRV_TEMPLATE
   25 activate service-template DefaultCriticalAccess_SRV_TEMPLATE
   30 authorize
   40 pause reauthentication
  20 class AAA_SVR_DOWN_AUTHD_HOST do-until-failure
   10 pause reauthentication
   20 authorize
  30 class MAB_FAILED do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
  40 class DOT1X_NO_RESP do-until-failure
   10 terminate dot1x
   20 authentication-restart 60
  50 class DOT1X_TIMEOUT do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  60 class always do-until-failure
   10 terminate mab
   20 terminate dot1x
   30 authentication-restart 60
 event aaa-available match-all
  10 class IN_CRITICAL_AUTH do-until-failure
   10 clear-session
  20 class NOT_IN_CRITICAL_AUTH do-until-failure
   10 resume reauthentication
 event agent-found match-all
  10 class always do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
 event inactivity-timeout match-all
  10 class always do-until-failure
   10 clear-session
 event authentication-success match-all
 event violation match-all
  10 class always do-until-failure
   10 restrict
 event authorization-failure match-all
  10 class AUTHC_SUCCESS-AUTHZ_FAIL do-until-failure
   10 authentication-restart 60
!
policy-map type control subscriber PMAP_DefaultWiredDot1xOpenAuth_1X_MAB
 event session-started match-all
  10 class always do-until-failure
   10 authenticate using dot1x retries 2 retry-time 0 priority 10
 event authentication-failure match-first
  5 class DOT1X_FAILED do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  10 class AAA_SVR_DOWN_UNAUTHD_HOST do-until-failure
   10 activate service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
   20 activate service-template DefaultCriticalVoice_SRV_TEMPLATE
   30 authorize
   40 pause reauthentication
  20 class AAA_SVR_DOWN_AUTHD_HOST do-until-failure
   10 pause reauthentication
   20 authorize
  30 class DOT1X_NO_RESP do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  40 class MAB_FAILED do-until-failure
   10 terminate mab
   20 authentication-restart 60
  50 class DOT1X_TIMEOUT do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  60 class always do-until-failure
   10 terminate dot1x
   20 terminate mab
   30 authentication-restart 60
 event aaa-available match-all
  10 class IN_CRITICAL_AUTH do-until-failure
   10 clear-session
  20 class NOT_IN_CRITICAL_AUTH do-until-failure
   10 resume reauthentication
 event agent-found match-all
  10 class always do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
 event inactivity-timeout match-all
  10 class always do-until-failure
   10 clear-session
 event authentication-success match-all
 event violation match-all
  10 class always do-until-failure
   10 restrict
 event authorization-failure match-all
  10 class AUTHC_SUCCESS-AUTHZ_FAIL do-until-failure
   10 authentication-restart 60
!
policy-map type control subscriber PMAP_DefaultWiredDot1xOpenAuth_MAB_1X
 event session-started match-all
  10 class always do-until-failure
   10 authenticate using mab priority 20
 event authentication-failure match-first
  5 class DOT1X_FAILED do-until-failure
   10 terminate dot1x
   20 authentication-restart 60
  10 class AAA_SVR_DOWN_UNAUTHD_HOST do-until-failure
   10 activate service-template DefaultCriticalAuthVlan_SRV_TEMPLATE
   20 activate service-template DefaultCriticalVoice_SRV_TEMPLATE
   30 authorize
   40 pause reauthentication
  20 class AAA_SVR_DOWN_AUTHD_HOST do-until-failure
   10 pause reauthentication
   20 authorize
  30 class MAB_FAILED do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
  40 class DOT1X_NO_RESP do-until-failure
   10 terminate dot1x
   20 authentication-restart 60
  50 class DOT1X_TIMEOUT do-until-failure
   10 terminate dot1x
   20 authenticate using mab priority 20
  60 class always do-until-failure
   10 terminate mab
   20 terminate dot1x
   30 authentication-restart 60
 event aaa-available match-all
  10 class IN_CRITICAL_AUTH do-until-failure
   10 clear-session
  20 class NOT_IN_CRITICAL_AUTH do-until-failure
   10 resume reauthentication
 event agent-found match-all
  10 class always do-until-failure
   10 terminate mab
   20 authenticate using dot1x retries 2 retry-time 0 priority 10
 event inactivity-timeout match-all
  10 class always do-until-failure
   10 clear-session
 event authentication-success match-all
 event violation match-all
  10 class always do-until-failure
   10 restrict
 event authorization-failure match-all
  10 class AUTHC_SUCCESS-AUTHZ_FAIL do-until-failure
   10 authentication-restart 60
!
policy-map system-cpp-policy
!
!
!
!
!
!
!
!
!
!
!
!
template DefaultWiredDot1xClosedAuth
 dot1x pae authenticator
 dot1x timeout supp-timeout 7
 dot1x max-req 3
 switchport mode access
 switchport voice vlan 2046
 mab
 access-session closed
 access-session port-control auto
 authentication periodic
 authentication timer reauthenticate server
 service-policy type control subscriber PMAP_DefaultWiredDot1xClosedAuth_1X_MAB
!
template DefaultWiredDot1xLowImpactAuth
 dot1x pae authenticator
 dot1x timeout supp-timeout 7
 dot1x max-req 3
 switchport mode access
 switchport voice vlan 2046
 mab
 access-session port-control auto
 authentication periodic
 authentication timer reauthenticate server
 service-policy type control subscriber PMAP_DefaultWiredDot1xLowImpactAuth_1X_MAB
!
template DefaultWiredDot1xOpenAuth
 dot1x pae authenticator
 dot1x timeout supp-timeout 7
 dot1x max-req 3
 switchport mode access
 switchport voice vlan 2046
 mab
 access-session port-control auto
 authentication periodic
 authentication timer reauthenticate server
 service-policy type control subscriber PMAP_DefaultWiredDot1xOpenAuth_1X_MAB
!
macro auto global processing
!
interface Loopback0
 ip address 10.4.255.3 255.255.255.255
 ip mtu 1496
 ip ospf 1 area 0
!
interface LISP0
!
interface LISP0.4099
!
interface L2LISP0
!
interface L2LISP0.8188
!
interface L2LISP0.8189
!
interface GigabitEthernet0/0
 vrf forwarding Mgmt-vrf
 no ip address
 negotiation auto
!
interface GigabitEthernet1/0/1
 no switchport
 ip address 10.4.3.2 255.255.255.0
 ip mtu 1496
 ip ospf 1 area 0
!
interface GigabitEthernet1/0/2
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/3
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/4
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/5
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/6
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/7
 switchport access vlan 10
 switchport mode access
 device-tracking attach-policy IPDT_POLICY
 load-interval 30
 no macro auto processing
 spanning-tree portfast
 spanning-tree bpduguard enable
!
interface GigabitEthernet1/0/8
 switchport access vlan 20
 switchport mode access
 device-tracking attach-policy IPDT_POLICY
 load-interval 30
 no macro auto processing
 spanning-tree portfast
 spanning-tree bpduguard enable
!
interface GigabitEthernet1/0/9
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/10
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/11
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/12
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/13
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/14
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/15
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/16
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/17
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/18
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/19
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/20
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/21
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/22
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/23
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/24
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/3
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/4
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/3
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/4
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/5
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/6
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/7
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/8
 device-tracking attach-policy IPDT_POLICY
!
interface FortyGigabitEthernet1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface FortyGigabitEthernet1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface TwentyFiveGigE1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface TwentyFiveGigE1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface AppGigabitEthernet1/0/1
!
interface Vlan1
 no ip address
!
interface Vlan10
 description Configured from Cisco DNA-Center
 mac-address 0000.0c9f.f9da
 vrf forwarding NJQYT_IT_VN
 ip address 10.4.10.1 255.255.255.0
 no ip redirects
 ip route-cache same-interface
 no lisp mobility liveness test
 lisp mobility NJQYT-IT-IPV4
!
interface Vlan20
 description Configured from Cisco DNA-Center
 mac-address 0000.0c9f.f06c
 vrf forwarding NJQYT_IT_VN
 ip address 10.4.20.1 255.255.255.0
 no ip redirects
 ip route-cache same-interface
 no lisp mobility liveness test
 lisp mobility NJQYT-Sales-IPV4
!
router lisp
 locator-table default
 locator-set rloc_ae09fda5-8050-48b1-b3f8-e2f41457c89d
  IPv4-interface Loopback0 priority 10 weight 10
  exit-locator-set
 !
 locator default-set rloc_ae09fda5-8050-48b1-b3f8-e2f41457c89d
 service ipv4
  encapsulation vxlan
  itr map-resolver 10.4.255.1
  etr map-server 10.4.255.1 key 7 1413430E0907297F7479616527475F4405
  etr map-server 10.4.255.1 proxy-reply
  etr
  sgt
  no map-cache away-eids send-map-request
  use-petr 10.4.255.1
  proxy-itr 10.4.255.3
  exit-service-ipv4
 !
 service ethernet
  itr map-resolver 10.4.255.1
  itr
  etr map-server 10.4.255.1 key 7 06025E24494D0A4D5546405B0950727922
  etr map-server 10.4.255.1 proxy-reply
  etr
  exit-service-ethernet
 !
 instance-id 4099
  remote-rloc-probe on-route-change
  dynamic-eid NJQYT-IT-IPV4
   database-mapping 10.4.10.0/24 locator-set rloc_ae09fda5-8050-48b1-b3f8-e2f41457c89d
   exit-dynamic-eid
  !
  dynamic-eid NJQYT-Sales-IPV4
   database-mapping 10.4.20.0/24 locator-set rloc_ae09fda5-8050-48b1-b3f8-e2f41457c89d
   exit-dynamic-eid
  !
  service ipv4
   eid-table vrf NJQYT_IT_VN
   map-cache 0.0.0.0/0 map-request
   exit-service-ipv4
  !
  exit-instance-id
 !
 instance-id 8188
  remote-rloc-probe on-route-change
  service ethernet
   eid-table vlan 10
   database-mapping mac locator-set rloc_ae09fda5-8050-48b1-b3f8-e2f41457c89d
   exit-service-ethernet
  !
  exit-instance-id
 !
 instance-id 8189
  remote-rloc-probe on-route-change
  service ethernet
   eid-table vlan 20
   database-mapping mac locator-set rloc_ae09fda5-8050-48b1-b3f8-e2f41457c89d
   exit-service-ethernet
  !
  exit-instance-id
 !
 ipv4 locator reachability minimum-mask-length 32 proxy-etr-only
 ipv4 source-locator Loopback0
 exit-router-lisp
!
router ospf 1
!
ip forward-protocol nd
ip http server
ip http secure-server
ip http client source-interface Loopback0
ip ssh source-interface Loopback0
ip ssh version 2
!
!
!
ip access-list extended IPV4_CRITICAL_AUTH_ACL
 10 permit ip any any
ip access-list extended IPV4_PRE_AUTH_ACL
 10 permit udp any any eq bootps
 20 permit udp any any eq bootpc
 30 permit udp any any eq domain
 40 deny ip any any
logging source-interface Loopback0
logging host 10.2.254.11
!
snmp-server community qytang RW
snmp-server trap-source Loopback0
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart
snmp-server enable traps flowmon
snmp-server enable traps entity-perf throughput-notif
snmp-server enable traps call-home message-send-fail server-fail
snmp-server enable traps tty
snmp-server enable traps eigrp
snmp-server enable traps ospf state-change
snmp-server enable traps ospf errors
snmp-server enable traps ospf retransmit
snmp-server enable traps ospf lsa
snmp-server enable traps ospf cisco-specific state-change nssa-trans-change
snmp-server enable traps ospf cisco-specific state-change shamlink interface
snmp-server enable traps ospf cisco-specific state-change shamlink neighbor
snmp-server enable traps ospf cisco-specific errors
snmp-server enable traps ospf cisco-specific retransmit
snmp-server enable traps ospf cisco-specific lsa
snmp-server enable traps bfd
snmp-server enable traps license
snmp-server enable traps smart-license
snmp-server enable traps auth-framework sec-violation
snmp-server enable traps rep
snmp-server enable traps memory bufferpeak
snmp-server enable traps energywise
snmp-server enable traps fru-ctrl
snmp-server enable traps entity
snmp-server enable traps flash insertion removal lowspace
snmp-server enable traps power-ethernet group 1 threshold 80
snmp-server enable traps power-ethernet police
snmp-server enable traps cpu threshold
snmp-server enable traps udld link-fail-rpt
snmp-server enable traps udld status-change
snmp-server enable traps vtp
snmp-server enable traps vlancreate
snmp-server enable traps vlandelete
snmp-server enable traps port-security
snmp-server enable traps envmon
snmp-server enable traps stackwise
snmp-server enable traps mvpn
snmp-server enable traps pw vc
snmp-server enable traps ipsla
snmp-server enable traps dhcp
snmp-server enable traps event-manager
snmp-server enable traps config-copy
snmp-server enable traps config
snmp-server enable traps config-ctid
snmp-server enable traps syslog
snmp-server enable traps ike policy add
snmp-server enable traps ike policy delete
snmp-server enable traps ike tunnel start
snmp-server enable traps ike tunnel stop
snmp-server enable traps ipsec cryptomap add
snmp-server enable traps ipsec cryptomap delete
snmp-server enable traps ipsec cryptomap attach
snmp-server enable traps ipsec cryptomap detach
snmp-server enable traps ipsec tunnel start
snmp-server enable traps ipsec tunnel stop
snmp-server enable traps ipsec too-many-sas
snmp-server enable traps ospfv3 state-change
snmp-server enable traps ospfv3 errors
snmp-server enable traps ipmulticast
snmp-server enable traps msdp
snmp-server enable traps pim neighbor-change rp-mapping-change invalid-pim-message
snmp-server enable traps bridge newroot topologychange
snmp-server enable traps stpx inconsistency root-inconsistency loop-inconsistency
snmp-server enable traps bgp cbgp2
snmp-server enable traps hsrp
snmp-server enable traps isis
snmp-server enable traps cef resource-failure peer-state-change peer-fib-state-change inconsistency
snmp-server enable traps lisp
snmp-server enable traps nhrp nhs
snmp-server enable traps nhrp nhc
snmp-server enable traps nhrp nhp
snmp-server enable traps nhrp quota-exceeded
snmp-server enable traps local-auth
snmp-server enable traps entity-diag boot-up-fail hm-test-recover hm-thresh-reached scheduled-test-fail
snmp-server enable traps mpls rfc ldp
snmp-server enable traps mpls ldp
snmp-server enable traps mpls rfc traffic-eng
snmp-server enable traps mpls traffic-eng
snmp-server enable traps mpls fast-reroute protected
snmp-server enable traps errdisable
snmp-server enable traps vlan-membership
snmp-server enable traps transceiver all
snmp-server enable traps bulkstat collection transfer
snmp-server enable traps mac-notification change move threshold
snmp-server enable traps vrfmib vrf-up vrf-down vnet-trunk-up vnet-trunk-down
snmp-server enable traps rf
snmp-server enable traps mpls vpn
snmp-server enable traps mpls rfc vpn
snmp-server host 10.2.254.11 version 2c qytang
!
!
ipv6 access-list IPV6_CRITICAL_AUTH_ACL
 sequence 10 permit ipv6 any any
!
ipv6 access-list IPV6_PRE_AUTH_ACL
 sequence 10 permit udp any any eq bootps
 sequence 20 permit udp any any eq bootpc
 sequence 30 permit udp any any eq domain
 sequence 40 deny ipv6 any any
!
control-plane
 service-policy input system-cpp-policy
!
!
line con 0
 stopbits 1
line vty 0 4
 login local
 transport input all
line vty 5 31
 login
 transport input ssh
!
ntp source Loopback0
ntp server 10.2.253.11
call-home
 ! If contact email address in call-home is configured as sch-smart-licensing@cisco.com
 ! the email address configured in Cisco Smart License Portal will be used as contact email address to send SCH notifications.
 contact-email-addr sch-smart-licensing@cisco.com
 profile "CiscoTAC-1"
  active
  destination transport-method http
!
!
!
!
!
!
telemetry ietf subscription 500
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_port_detail
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 501
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_module
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 502
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_stack
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 503
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_switch
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 504
 encoding encode-tdl
 filter nested-uri /services;serviceName=ios_oper/platform_component;cname=0?platform_properties
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 30000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 550
 encoding encode-tdl
 filter tdl-uri /services;serviceName=smevent/sessionevent
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 551
 encoding encode-tdl
 filter tdl-uri /services;serviceName=sessmgr_oper/session_context_data
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 552
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/sisf_mac_oper_state
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 553
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/sisf_db_wired_mac
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 554
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/cdp_neighbor_detail
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 555
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/cdp_neighbor_detail
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 600
 encoding encode-tdl
 filter tdl-uri /services;serviceName=sessmgr_oper/tbl_aaa_servers_stat
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 601
 encoding encode-tdl
 filter tdl-uri /services;serviceName=sessmgr_oper/tbl_aaa_servers_stat
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 602
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_emul_oper/lisp_routers;top_id=0/sessions
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 603
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/lisp_tcp_session_state
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 604
 encoding encode-tdl
 filter nested-uri /services;serviceName=ios_emul_oper/lisp_routers;top_id=0/instances;iid=0/af;iaftype=LISP_TDL_IAF_IPV4/lisp_publisher
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 605
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/lisp_pubsub_session_state
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 606
 encoding encode-tdl
 filter nested-uri /services;serviceName=ios_emul_oper/lisp_routers;top_id=0/remote_locator_sets;name=default-etr-locator-set-ipv4/rem_loc_set_rlocs_si
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 607
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/lisp_etr_si_type
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 750
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_emul_oper/environment_sensor
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 30000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 751
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/platform_component
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 30000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 1020
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/install_status
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 8882
 encoding encode-tdl
 filter tdl-transform trustSecCounterDelta
 receiver-type protocol
 source-address 10.4.255.3
 stream native
 update-policy periodic 90000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry receiver protocol DNAC_ASSURANCE_RECEIVER
 host ip-address 10.2.254.11 25103
 protocol tls-native profile sdn-network-infra-iwan
telemetry transform trustSecCounterDelta
 input table cts_rolebased_policy
  field dst_sgt
  field src_sgt
  field sgacl_name
  field monitor_mode
  field num_of_sgacl
  field policy_life_time
  field total_deny_count
  field last_updated_time
  field total_permit_count
  join-key cts_role_based_policy_key
  logical-op and
  type mandatory
  uri /services;serviceName=ios_emul_oper/cts_rolebased_policy
 operation 1
  output-field 1
   field cts_rolebased_policy.src_sgt
  output-field 2
   field cts_rolebased_policy.dst_sgt
  output-field 3
   field cts_rolebased_policy.total_permit_count
   output-op type delta
  output-field 4
   field cts_rolebased_policy.total_deny_count
   output-op type delta
  output-field 5
   field cts_rolebased_policy.sgacl_name
  output-field 6
   field cts_rolebased_policy.monitor_mode
  output-field 7
   field cts_rolebased_policy.num_of_sgacl
  output-field 8
   field cts_rolebased_policy.policy_life_time
  output-field 9
   field cts_rolebased_policy.last_updated_time
 specified
netconf-yang
end

SW402#
SW402#
SW402#
SW402#
SW402#
SW402#
SW402#
SW402#
SW402#





SW400>
SW400>en
Password:
SW400#sho run
Building configuration...

Current configuration : 32753 bytes
!
! Last configuration change at 08:48:21 UTC Fri Aug 14 2026 by qytang
!
version 17.8
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
! Call-home is enabled by Smart-Licensing.
service call-home
platform punt-keepalive disable-kernel-core
!
hostname SW400
!
!
vrf definition Mgmt-vrf
 !
 address-family ipv4
 exit-address-family
 !
 address-family ipv6
 exit-address-family
!
vrf definition NJQYT_IT_VN
 rd 1:4099
 !
 address-family ipv4
  route-target export 1:4099
  route-target import 1:4099
 exit-address-family
!
no aaa new-model
switch 1 provision c9300-24u
!
!
!
!
ip routing
!
!
!
!
!
ip name-server 10.2.253.11
ip domain lookup source-interface Loopback0
ip domain name qytang.com
!
!
!
login on-success log
vtp mode transparent
!
!
!
!
!
!
!
mpls label mode all-vrfs protocol all-afs per-vrf
!
flow exporter 10.2.254.11
 destination 10.2.254.11
 transport udp 6007
!
device-tracking tracking
!
device-tracking policy IPDT_POLICY
 no protocol udp
 tracking enable
!
!
!
crypto pki trustpoint SLA-TrustPoint
 enrollment pkcs12
 revocation-check crl
!
crypto pki trustpoint TP-self-signed-1519330609
 enrollment selfsigned
 subject-name cn=IOS-Self-Signed-Certificate-1519330609
 revocation-check none
 rsakeypair TP-self-signed-1519330609
!
crypto pki trustpoint DNAC-CA
 enrollment mode ra
 enrollment terminal
 usage ssl-client
 revocation-check crl none
 source interface Loopback0
!
crypto pki trustpoint sdn-network-infra-iwan
 enrollment url http://10.2.254.11:80/ejbca/publicweb/apply/scep/sdnscep
 fqdn Switch.qytang.com
 subject-name CN=C9300-24U_FCW2149L0AW_sdn-network-infra-iwan
 subject-alt-name Switch.qytang.com
 revocation-check crl
 source interface Loopback0
 rsakeypair sdn-network-infra-iwan
 auto-enroll 80 regenerate
!
!
crypto pki certificate chain SLA-TrustPoint
 certificate ca 01
  30820321 30820209 A0030201 02020101 300D0609 2A864886 F70D0101 0B050030
  32310E30 0C060355 040A1305 43697363 6F312030 1E060355 04031317 43697363
  6F204C69 63656E73 696E6720 526F6F74 20434130 1E170D31 33303533 30313934
  3834375A 170D3338 30353330 31393438 34375A30 32310E30 0C060355 040A1305
  43697363 6F312030 1E060355 04031317 43697363 6F204C69 63656E73 696E6720
  526F6F74 20434130 82012230 0D06092A 864886F7 0D010101 05000382 010F0030
  82010A02 82010100 A6BCBD96 131E05F7 145EA72C 2CD686E6 17222EA1 F1EFF64D
  CBB4C798 212AA147 C655D8D7 9471380D 8711441E 1AAF071A 9CAE6388 8A38E520
  1C394D78 462EF239 C659F715 B98C0A59 5BBB5CBD 0CFEBEA3 700A8BF7 D8F256EE
  4AA4E80D DB6FD1C9 60B1FD18 FFC69C96 6FA68957 A2617DE7 104FDC5F EA2956AC
  7390A3EB 2B5436AD C847A2C5 DAB553EB 69A9A535 58E9F3E3 C0BD23CF 58BD7188
  68E69491 20F320E7 948E71D7 AE3BCC84 F10684C7 4BC8E00F 539BA42B 42C68BB7
  C7479096 B4CB2D62 EA2F505D C7B062A4 6811D95B E8250FC4 5D5D5FB8 8F27D191
  C55F0D76 61F9A4CD 3D992327 A8BB03BD 4E6D7069 7CBADF8B DF5F4368 95135E44
  DFC7C6CF 04DD7FD1 02030100 01A34230 40300E06 03551D0F 0101FF04 04030201
  06300F06 03551D13 0101FF04 05300301 01FF301D 0603551D 0E041604 1449DC85
  4B3D31E5 1B3E6A17 606AF333 3D3B4C73 E8300D06 092A8648 86F70D01 010B0500
  03820101 00507F24 D3932A66 86025D9F E838AE5C 6D4DF6B0 49631C78 240DA905
  604EDCDE FF4FED2B 77FC460E CD636FDB DD44681E 3A5673AB 9093D3B1 6C9E3D8B
  D98987BF E40CBD9E 1AECA0C2 2189BB5C 8FA85686 CD98B646 5575B146 8DFC66A8
  467A3DF4 4D565700 6ADF0F0D CF835015 3C04FF7C 21E878AC 11BA9CD2 55A9232C
  7CA7B7E6 C1AF74F6 152E99B7 B1FCF9BB E973DE7F 5BDDEB86 C71E3B49 1765308B
  5FB0DA06 B92AFE7F 494E8A9E 07B85737 F3A58BE1 1A48A229 C37C1E69 39F08678
  80DDCD16 D6BACECA EEBC7CF9 8428787B 35202CDC 60E4616A B623CDBD 230E3AFB
  418616A9 4093E049 4D10AB75 27E86F73 932E35B5 8862FDAE 0275156F 719BB2F0
  D697DF7F 28
        quit
crypto pki certificate chain TP-self-signed-1519330609
 certificate self-signed 01
  30820330 30820218 A0030201 02020101 300D0609 2A864886 F70D0101 05050030
  31312F30 2D060355 04031326 494F532D 53656C66 2D536967 6E65642D 43657274
  69666963 6174652D 31353139 33333036 3039301E 170D3236 30383133 30393432
  33355A17 0D333630 38313230 39343233 355A3031 312F302D 06035504 03132649
  4F532D53 656C662D 5369676E 65642D43 65727469 66696361 74652D31 35313933
  33303630 39308201 22300D06 092A8648 86F70D01 01010500 0382010F 00308201
  0A028201 0100C18D 03682BBB FF3BF122 142FB7F1 5DF0DD64 D3B70A88 DF6B52F9
  21EF8E6F 37850480 0044611F 193E2CAD 0DEAA777 7455BA9D C5564398 F85FC420
  496875A5 BE7B4E96 67BDA3B6 519AE59C 4C6733CF 83409C17 498478B0 DB27CA16
  FA22BA62 ED26767B D18D290B 2D704E20 43CC6E9B F2747B7A 0C080EC8 282D2FC7
  D9C28550 2E12A569 89983AB0 8F6A7DD7 0F7B6893 79979F5E 3F12A93B E5D2799A
  32456AB2 6E65124F B275ECBB 1A6C7359 EEE8C0B3 22C46146 63275561 E4755CB7
  92B544F0 B844D1EB 286CB621 C0AC19F0 4F5F807E FE263D34 D73CD056 044B931F
  5053918F 70F41A38 242A3EE2 9DDBA7F5 A98EB88B EDA9E2E1 62B00184 631ACDCB
  617C6E1B 7F110203 010001A3 53305130 0F060355 1D130101 FF040530 030101FF
  301F0603 551D2304 18301680 14B447A4 6925E2B1 213D3FB8 6D015565 6C3ACDA6
  66301D06 03551D0E 04160414 B447A469 25E2B121 3D3FB86D 0155656C 3ACDA666
  300D0609 2A864886 F70D0101 05050003 82010100 7F770276 59DD9624 CFB1F063
  58D499AE F67E06AE 774435EF 2BAA1ACE B9FD5F44 A4610F75 1E635842 1EA10C27
  D2C013C6 367326A9 00E26441 6C80BA98 5842ED54 569E4CFC 3CDA69F4 8BDF2BED
  F0FA9808 F26E7521 AFD83B68 061C1C23 E0DD5568 BBB7F8F9 DB98BD3F 661CD1D7
  AFDA7F59 D9DF0735 B2B49B66 DABF9939 7877AA34 169E6996 4C9C040E CAB0FC94
  D361FF7F B709B24D 6B98668A B6B2E1C1 00D6F4F0 D38EC621 977AE298 DB23061B
  E2618534 B6450A08 A98099D6 40278115 FC0AB506 6EFBE5C5 3AA4AE41 A01F0909
  C958DA57 284FF517 1F635A69 8F9F1290 1808FB1D 3FAD8BD3 14B09474 6379EA89
  4150C325 73B98144 DEE0EEC0 D8A7CDA8 4C9B14D8
        quit
crypto pki certificate chain DNAC-CA
 certificate ca 3F2A343E086C62299086E98277D81F0F1AB65DFF
  308203A5 3082028D A0030201 0202143F 2A343E08 6C622990 86E98277 D81F0F1A
  B65DFF30 0D06092A 864886F7 0D01010B 05003062 312D302B 06035504 030C2461
  33653730 3138322D 61306535 2D363331 342D6363 65612D62 35353162 35306131
  64663931 16301406 0355040A 0C0D4369 73636F20 53797374 656D7331 19301706
  0355040B 0C104369 73636F20 444E4120 43656E74 6572301E 170D3236 30343132
  30393532 34345A17 0D323930 31303630 39353234 345A3062 312D302B 06035504
  030C2461 33653730 3138322D 61306535 2D363331 342D6363 65612D62 35353162
  35306131 64663931 16301406 0355040A 0C0D4369 73636F20 53797374 656D7331
  19301706 0355040B 0C104369 73636F20 444E4120 43656E74 65723082 0122300D
  06092A86 4886F70D 01010105 00038201 0F003082 010A0282 010100C2 87898047
  48DCC8BD 98E768EC B28C610A 2B0401F7 D934A918 88045794 A8B389E1 2F1F3665
  A74843C8 92BA2569 545DDB5B EFCC51F8 6496A6DB 33074488 024694D0 6130CC1B
  5DA74746 E9BF21EA ECD68658 4E516BFE 44C3E8AF 7D28E377 D37B5F2E CA406D55
  BC54CCE4 C26D90C2 9805F585 3CFC2807 B30A6657 3A9607C9 01B1563F 07B5BD54
  58B14A05 8C396C53 B94AFBA9 0ACC5C2F 24718251 48A852A6 DB5873C1 F5850DF6
  E8517DEE 47D4A5B7 BF23AE75 F5B2301E C610EC1A A4512BD1 93AA7C16 940428DB
  C0D0999A F04AF5BF 388F2949 39E4915D 79602302 A59E8AF0 3CBB46BB 238113B5
  85B388F8 97A6E04E 33BD2D6E A5C18759 36B137AB E1A22083 6F933B02 03010001
  A3533051 301D0603 551D0E04 16041485 B2BD1B41 A3FAF964 445F58E3 33601A65
  53D9FE30 1F060355 1D230418 30168014 85B2BD1B 41A3FAF9 64445F58 E333601A
  6553D9FE 300F0603 551D1301 01FF0405 30030101 FF300D06 092A8648 86F70D01
  010B0500 03820101 0053B628 525AF621 446B630A CBCCF07A B16BAE20 E92AAA5B
  A4B72DFB 88CBB2B4 A44BD68A F7621278 706B5DCD C120E30D 7702DDC9 F0D64C2D
  3E616AEB 2E88626C 76A1C029 81BD5F7E C86FB2A4 D202E9F3 6EBECD24 FB2EB87A
  EBD80036 410EECB3 BE612C9F 79B723B8 9E72B8F8 23DCCBE5 C9A685A3 A10A5B0A
  ABA840E6 8C35EFE3 BE6B358A 23441C80 ACA2BA94 AD5157D7 426ADC26 1E8AC742
  EC48DF24 E1A1B145 6D60DE5F 8E5B13FC 19508072 F5EF3FEF 67A881F6 AB9B4255
  96FA72D2 1BCFFFD0 2B4C6E5C 4F4D9D51 9C500D0E 0915860E D6A4C2AB 6F74B721
  46BBD065 F0AAADA4 317F5481 BFCFB9FF 4200AF1E 105E778E 526AE743 4FE0091E
  BF98EB7F 9F5BD0EB 8C
        quit
crypto pki certificate chain sdn-network-infra-iwan
 certificate 4772618765A55C67
  30820379 30820261 A0030201 02020847 72618765 A55C6730 0D06092A 864886F7
  0D01010D 0500301F 311D301B 06035504 030C1473 646E2D6E 6574776F 726B2D69
  6E667261 2D636130 1E170D32 36303831 34303532 3534395A 170D3237 30383134
  30353235 34395A30 59312030 1E06092A 864886F7 0D010902 0C115377 69746368
  2E717974 616E672E 636F6D31 35303306 03550403 0C2C4339 3330302D 3234555F
  46435732 3134394C 3041575F 73646E2D 6E657477 6F726B2D 696E6672 612D6977
  616E3082 0122300D 06092A86 4886F70D 01010105 00038201 0F003082 010A0282
  010100BC 7CC66AD9 FF93B770 52CA2ECE 806C081A 00C6BB90 F54D3E02 529A6452
  82886DE1 ABA40235 93D05CDE 598D9E91 1450E316 9DE41119 E99AD74E F914541A
  F0587C2B 0EDECAC1 92026C87 52644382 180F9E61 623B394F FF7AB949 A8080E21
  44B4C54E FD1D4B27 3AE007E3 BF97F595 34CB2BF8 10905C3A 05988B20 662F9226
  84861F1C 2180BE2B 9EBCA7C2 57DA6B7D B75295D5 E3EA60C8 4DBEE328 D3C6C19D
  FAF14212 DAA5D489 E0117FA6 6B024E4D 08602017 A7C1CC68 08830626 9EEA2333
  34A7C4C2 C7C82A0A 8719792F AAB37AD6 D7518633 8113F84E 90EA2FA7 0CEE8618
  11040382 1FA43623 5B4DA5C0 A293D725 141F113C F6608134 FD74FF33 155B0EA2
  A578CD02 03010001 A37F307D 300C0603 551D1301 01FF0402 3000301F 0603551D
  23041830 168014F3 D815BC93 BBACD230 82661FC5 764D0EE4 C0654C30 1D060355
  1D250416 30140608 2B060105 05070302 06082B06 01050507 0304301D 0603551D
  0E041604 1422F5EB B196BB21 120A23DE C67B8BFD BDBEBCB7 53300E06 03551D0F
  0101FF04 04030205 E0300D06 092A8648 86F70D01 010D0500 03820101 0086EB1B
  2A56605D EC24E2CA 991FC4BD 4578B0C2 077DC125 66204A2B 7DBE640C FE749C43
  CC6FF6B2 5DD9B567 79C10D00 3F96FD3C 657E10BD B6DBF518 49EDE1C5 AA134074
  C1ECAD2D AE985C70 6CF5DA6E 007E64F9 F8A8F8E7 F9BD4CD0 E8A878D9 A6873C11
  73007481 6F4B7338 A7405574 2392A5C1 93A638E4 7E963911 CB27A77D 85CBC3B0
  7DD1F3C6 FFD67834 B29D8E50 C9938FC3 DFC11640 8E12EAB8 E6F28DB7 B71E7CB2
  2B836F1B 903D6C6A 691E772E F1DD240E 5D6BB33E DE979835 C4B56D24 3C0BBC17
  A1EAAD98 458366F4 512A4BF8 22CFBE16 0441C886 94502FC8 B02867B7 AEA0232D
  9FAFB046 4B69EC46 DC5BB97A 1092D4BB DE66B31E 576476A1 781C809A F2
        quit
 certificate ca 0D2C599F6B4F3C3B
  30820323 3082020B A0030201 0202080D 2C599F6B 4F3C3B30 0D06092A 864886F7
  0D01010D 0500301F 311D301B 06035504 030C1473 646E2D6E 6574776F 726B2D69
  6E667261 2D636130 1E170D32 36303431 32313634 3432385A 170D3431 30343132
  31363434 32385A30 1F311D30 1B060355 04030C14 73646E2D 6E657477 6F726B2D
  696E6672 612D6361 30820122 300D0609 2A864886 F70D0101 01050003 82010F00
  3082010A 02820101 00DFA802 62BA5139 D4D1E41F 9C596440 861E5A7E 26762783
  05887FE5 A6266FBA F8D17E6D 203A2AC6 2E89C4AC C09320D2 5321ADF3 8F896873
  5B8A1D72 B2622933 8DA1CEBC EB055C22 75F320A0 B689DF92 B4D5707B EE875BC2
  3A1B2319 CBE23264 8DF9E3BA 396519E7 118424E9 43FC7005 6EAE181B E509E0AE
  155D2065 839CED8C BF907B36 098D7852 01056286 79207C09 F0F3D035 9F89B9C9
  94A4B792 77B35C28 382DE32F ABA4D514 60BAD7A3 541B8197 BBA6C8A8 D5D3449A
  E35546B7 B451C0D2 8B2AB5E1 43477F03 34CBE376 FC5D6EDE E20C9A60 F28406A5
  06570104 81EC1EA8 353ECC6F 4C9F7839 BBE535DE 15BC4D1B 71C3A73B F676ABC3
  FF47A7A7 2A05A892 67020301 0001A363 3061300F 0603551D 130101FF 04053003
  0101FF30 1F060355 1D230418 30168014 F3D815BC 93BBACD2 3082661F C5764D0E
  E4C0654C 301D0603 551D0E04 160414F3 D815BC93 BBACD230 82661FC5 764D0EE4
  C0654C30 0E060355 1D0F0101 FF040403 02018630 0D06092A 864886F7 0D01010D
  05000382 0101007B 23A88C34 04AB840F FBBB2B5A E9CF6E2A 3466D68E 0CEE4C64
  13C7E4F3 2316397D E8A7633B 0F533EE5 BAB6AB19 8962AB73 191107F6 0FF41D68
  F095866A A2A448AE EB4B274A B3B5E3DD 070E7BF2 5FFE4C2C FBC542FC E4ABF9D5
  821013CA 300DE191 65DD8389 C6F59515 039B1FC6 5118CC9B 6CA30786 2C35E709
  547ED3D5 51B7D7F6 59B1C00D B0717859 42998C71 8902B9D4 F1E5A428 3CE21FF9
  CD34AD3D 230FBE93 8F02522A D3613A9C 51DDDB72 A4E26408 24265C47 7BC00FFC
  E80AE026 66A2C5C7 FAF255A0 D841F886 FD97ACD1 7817BDA8 24EDC954 1010C506
  6D466022 EE2D14B0 C7DC24B8 E2666845 CD6AEC8B E2FE5560 E41B7D16 6DDD5FCE
  64D5075E 5EE6B6
        quit
!
!
license boot level network-advantage addon dna-advantage
license smart transport off
diagnostic bootup level minimal
memory free low-watermark processor 131046
!
!
!
!
spanning-tree mode rapid-pvst
spanning-tree extend system-id
!
enable password 7 061716354D400E
!
username qytang privilege 15 password 7 14060B1F0D0A2D
!
redundancy
 mode sso
crypto engine compliance shield disable
!
!
!
!
!
transceiver type all
 monitoring
!
vlan 999
!
!
class-map match-any system-cpp-police-ewlc-control
  description EWLC Control
class-map match-any system-cpp-police-topology-control
  description Topology control
class-map match-any system-cpp-police-sw-forward
  description Sw forwarding, L2 LVX data packets, LOGGING, Transit Traffic
class-map match-any system-cpp-default
  description EWLC Data, Inter FED Traffic
class-map match-any system-cpp-police-sys-data
  description Openflow, Exception, EGR Exception, NFL Sampled Data, RPF Failed
class-map match-any system-cpp-police-punt-webauth
  description Punt Webauth
class-map match-any system-cpp-police-l2lvx-control
  description L2 LVX control packets
class-map match-any system-cpp-police-forus
  description Forus Address resolution and Forus traffic
class-map match-any system-cpp-police-multicast-end-station
  description MCAST END STATION
class-map match-any system-cpp-police-high-rate-app
  description High Rate Applications
class-map match-any system-cpp-police-multicast
  description MCAST Data
class-map match-any system-cpp-police-l2-control
  description L2 control
class-map match-any system-cpp-police-dot1x-auth
  description DOT1X Auth
class-map match-any system-cpp-police-data
  description ICMP redirect, ICMP_GEN and BROADCAST
class-map match-any system-cpp-police-stackwise-virt-control
  description Stackwise Virtual OOB
class-map match-any non-client-nrt-class
class-map match-any system-cpp-police-routing-control
  description Routing control and Low Latency
class-map match-any system-cpp-police-protocol-snooping
  description Protocol snooping
class-map match-any system-cpp-police-dhcp-snooping
  description DHCP snooping
class-map match-any system-cpp-police-ios-routing
  description L2 control, Topology control, Routing control, Low Latency
class-map match-any system-cpp-police-system-critical
  description System Critical and Gold Pkt
class-map match-any system-cpp-police-ios-feature
  description ICMPGEN,BROADCAST,ICMP,L2LVXCntrl,ProtoSnoop,PuntWebauth,MCASTData,Transit,DOT1XAuth,Swfwd,LOGGING,L2LVXData,ForusTraffic,ForusARP,McastEndStn,Openflow,Exception,EGRExcption,NflSampled,RpfFailed
!
policy-map system-cpp-policy
!
!
!
!
!
!
!
!
!
!
!
!
interface Loopback0
 ip address 10.4.255.1 255.255.255.255
 ip mtu 1496
 ip ospf 1 area 0
!
interface Loopback10
 description Loopback Border
 vrf forwarding NJQYT_IT_VN
 ip address 10.4.10.1 255.255.255.255
!
interface Loopback20
 description Loopback Border
 vrf forwarding NJQYT_IT_VN
 ip address 10.4.20.1 255.255.255.255
!
interface LISP0
!
interface LISP0.4099
!
interface GigabitEthernet0/0
 vrf forwarding Mgmt-vrf
 no ip address
 negotiation auto
!
interface GigabitEthernet1/0/1
 no switchport
 ip address 10.4.1.2 255.255.255.0
 ip mtu 1496
 ip ospf network point-to-point
 ip ospf 1 area 0
!
interface GigabitEthernet1/0/2
 no switchport
 ip address 10.4.2.1 255.255.255.0
 ip mtu 1496
 ip ospf 1 area 0
!
interface GigabitEthernet1/0/3
 no switchport
 ip address 10.4.3.1 255.255.255.0
 ip mtu 1496
 ip ospf 1 area 0
!
interface GigabitEthernet1/0/4
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/5
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/6
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/7
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/8
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/9
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/10
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/11
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/12
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/13
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/14
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/15
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/16
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/17
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/18
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/19
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/20
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/21
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/22
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/23
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/0/24
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/3
 device-tracking attach-policy IPDT_POLICY
!
interface GigabitEthernet1/1/4
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/3
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/4
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/5
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/6
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/7
 device-tracking attach-policy IPDT_POLICY
!
interface TenGigabitEthernet1/1/8
 device-tracking attach-policy IPDT_POLICY
!
interface FortyGigabitEthernet1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface FortyGigabitEthernet1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface TwentyFiveGigE1/1/1
 device-tracking attach-policy IPDT_POLICY
!
interface TwentyFiveGigE1/1/2
 device-tracking attach-policy IPDT_POLICY
!
interface AppGigabitEthernet1/0/1
!
interface Vlan1
 no ip address
!
router lisp
 locator-table default
 locator-set rloc_e47ab85e-f0c7-411a-882b-6da351924b27
  IPv4-interface Loopback0 priority 10 weight 10
  auto-discover-rlocs
  exit-locator-set
 !
 locator default-set rloc_e47ab85e-f0c7-411a-882b-6da351924b27
 service ipv4
  encapsulation vxlan
  itr map-resolver 10.4.255.1
  etr map-server 10.4.255.1 key 7 0202555E0E050C751C1F5B4900434A590A
  etr map-server 10.4.255.1 proxy-reply
  etr
  sgt
  no map-cache away-eids send-map-request
  proxy-etr
  proxy-itr 10.4.255.1
  map-server
  map-resolver
  exit-service-ipv4
 !
 service ethernet
  itr map-resolver 10.4.255.1
  itr
  etr map-server 10.4.255.1 key 7 00004203015808525F701E1E0C4D5D4514
  etr map-server 10.4.255.1 proxy-reply
  etr
  map-server
  map-resolver
  exit-service-ethernet
 !
 instance-id 4099
  remote-rloc-probe on-route-change
  service ipv4
   eid-table vrf NJQYT_IT_VN
   route-export site-registrations
   distance site-registrations 250
   map-cache site-registration
   exit-service-ipv4
  !
  exit-instance-id
 !
 site site_uci
  description map-server configured from Cisco DNA-Center
  authentication-key 7 1413430E0907297F7479616527475F4405
  eid-record instance-id 4099 10.4.10.0/24 accept-more-specifics
  eid-record instance-id 4099 10.4.20.0/24 accept-more-specifics
  eid-record instance-id 8188 any-mac
  eid-record instance-id 8189 any-mac
  exit-site
 !
 ipv4 locator reachability exclude-default
 ipv4 source-locator Loopback0
 exit-router-lisp
!
router ospf 1
!
router bgp 65004
 bgp router-id interface Loopback0
 bgp log-neighbor-changes
 bgp graceful-restart
 !
 address-family ipv4 vrf NJQYT_IT_VN
  bgp aggregate-timer 0
  network 10.4.10.1 mask 255.255.255.255
  network 10.4.20.1 mask 255.255.255.255
  aggregate-address 10.4.20.0 255.255.255.0 summary-only
  aggregate-address 10.4.10.0 255.255.255.0 summary-only
  redistribute lisp metric 10
 exit-address-family
!
ip forward-protocol nd
ip http server
ip http secure-server
ip http client source-interface Loopback0
ip ssh source-interface Loopback0
ip ssh version 2
!
ip community-list 1 permit 655370
!
!
ip prefix-list deny_0.0.0.0 seq 10 permit 0.0.0.0/0
!
logging source-interface Loopback0
logging host 10.2.254.11
!
route-map deny_0.0.0.0 deny 25
 match ip address prefix-list deny_0.0.0.0
!
route-map deny_0.0.0.0 permit 30
!
snmp-server community qytang RW
snmp-server trap-source Loopback0
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart
snmp-server enable traps flowmon
snmp-server enable traps entity-perf throughput-notif
snmp-server enable traps call-home message-send-fail server-fail
snmp-server enable traps tty
snmp-server enable traps eigrp
snmp-server enable traps ospf state-change
snmp-server enable traps ospf errors
snmp-server enable traps ospf retransmit
snmp-server enable traps ospf lsa
snmp-server enable traps ospf cisco-specific state-change nssa-trans-change
snmp-server enable traps ospf cisco-specific state-change shamlink interface
snmp-server enable traps ospf cisco-specific state-change shamlink neighbor
snmp-server enable traps ospf cisco-specific errors
snmp-server enable traps ospf cisco-specific retransmit
snmp-server enable traps ospf cisco-specific lsa
snmp-server enable traps bfd
snmp-server enable traps license
snmp-server enable traps smart-license
snmp-server enable traps auth-framework sec-violation
snmp-server enable traps rep
snmp-server enable traps memory bufferpeak
snmp-server enable traps energywise
snmp-server enable traps fru-ctrl
snmp-server enable traps entity
snmp-server enable traps flash insertion removal lowspace
snmp-server enable traps power-ethernet group 1 threshold 80
snmp-server enable traps power-ethernet police
snmp-server enable traps cpu threshold
snmp-server enable traps udld link-fail-rpt
snmp-server enable traps udld status-change
snmp-server enable traps vtp
snmp-server enable traps vlancreate
snmp-server enable traps vlandelete
snmp-server enable traps port-security
snmp-server enable traps envmon
snmp-server enable traps stackwise
snmp-server enable traps mvpn
snmp-server enable traps pw vc
snmp-server enable traps ipsla
snmp-server enable traps dhcp
snmp-server enable traps event-manager
snmp-server enable traps config-copy
snmp-server enable traps config
snmp-server enable traps config-ctid
snmp-server enable traps syslog
snmp-server enable traps ike policy add
snmp-server enable traps ike policy delete
snmp-server enable traps ike tunnel start
snmp-server enable traps ike tunnel stop
snmp-server enable traps ipsec cryptomap add
snmp-server enable traps ipsec cryptomap delete
snmp-server enable traps ipsec cryptomap attach
snmp-server enable traps ipsec cryptomap detach
snmp-server enable traps ipsec tunnel start
snmp-server enable traps ipsec tunnel stop
snmp-server enable traps ipsec too-many-sas
snmp-server enable traps ospfv3 state-change
snmp-server enable traps ospfv3 errors
snmp-server enable traps ipmulticast
snmp-server enable traps msdp
snmp-server enable traps pim neighbor-change rp-mapping-change invalid-pim-message
snmp-server enable traps bridge newroot topologychange
snmp-server enable traps stpx inconsistency root-inconsistency loop-inconsistency
snmp-server enable traps bgp cbgp2
snmp-server enable traps hsrp
snmp-server enable traps isis
snmp-server enable traps cef resource-failure peer-state-change peer-fib-state-change inconsistency
snmp-server enable traps lisp
snmp-server enable traps nhrp nhs
snmp-server enable traps nhrp nhc
snmp-server enable traps nhrp nhp
snmp-server enable traps nhrp quota-exceeded
snmp-server enable traps local-auth
snmp-server enable traps entity-diag boot-up-fail hm-test-recover hm-thresh-reached scheduled-test-fail
snmp-server enable traps mpls rfc ldp
snmp-server enable traps mpls ldp
snmp-server enable traps mpls rfc traffic-eng
snmp-server enable traps mpls traffic-eng
snmp-server enable traps mpls fast-reroute protected
snmp-server enable traps errdisable
snmp-server enable traps vlan-membership
snmp-server enable traps transceiver all
snmp-server enable traps bulkstat collection transfer
snmp-server enable traps mac-notification change move threshold
snmp-server enable traps vrfmib vrf-up vrf-down vnet-trunk-up vnet-trunk-down
snmp-server enable traps rf
snmp-server enable traps mpls vpn
snmp-server enable traps mpls rfc vpn
snmp-server host 10.2.254.11 version 2c qytang
!
!
control-plane
 service-policy input system-cpp-policy
!
!
line con 0
 stopbits 1
line vty 0 4
 login local
 transport input all
line vty 5 31
 login
 transport input ssh
!
ntp source Loopback0
ntp server 10.2.253.11
call-home
 ! If contact email address in call-home is configured as sch-smart-licensing@cisco.com
 ! the email address configured in Cisco Smart License Portal will be used as contact email address to send SCH notifications.
 contact-email-addr sch-smart-licensing@cisco.com
 profile "CiscoTAC-1"
  active
  destination transport-method http
!
!
!
!
!
!
telemetry ietf subscription 500
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_port_detail
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 501
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_module
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 502
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_stack
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 503
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/poe_switch
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 504
 encoding encode-tdl
 filter nested-uri /services;serviceName=ios_oper/platform_component;cname=0?platform_properties
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 30000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 550
 encoding encode-tdl
 filter tdl-uri /services;serviceName=smevent/sessionevent
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 551
 encoding encode-tdl
 filter tdl-uri /services;serviceName=sessmgr_oper/session_context_data
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 552
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/sisf_mac_oper_state
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 553
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/sisf_db_wired_mac
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 554
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/cdp_neighbor_detail
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 555
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/cdp_neighbor_detail
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 600
 encoding encode-tdl
 filter tdl-uri /services;serviceName=sessmgr_oper/tbl_aaa_servers_stat
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 60000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 601
 encoding encode-tdl
 filter tdl-uri /services;serviceName=sessmgr_oper/tbl_aaa_servers_stat
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 602
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_emul_oper/lisp_routers;top_id=0/sessions
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 603
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/lisp_tcp_session_state
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 604
 encoding encode-tdl
 filter nested-uri /services;serviceName=ios_emul_oper/lisp_routers;top_id=0/instances;iid=0/af;iaftype=LISP_TDL_IAF_IPV4/lisp_publisher
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 605
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/lisp_pubsub_session_state
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 606
 encoding encode-tdl
 filter nested-uri /services;serviceName=ios_emul_oper/lisp_routers;top_id=0/remote_locator_sets;name=default-etr-locator-set-ipv4/rem_loc_set_rlocs_si
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 360000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 607
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/lisp_etr_si_type
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 750
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_emul_oper/environment_sensor
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 30000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 751
 encoding encode-tdl
 filter tdl-uri /services;serviceName=ios_oper/platform_component
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 30000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 1020
 encoding encode-tdl
 filter tdl-uri /services;serviceName=iosevent/install_status
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy on-change
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry ietf subscription 8882
 encoding encode-tdl
 filter tdl-transform trustSecCounterDelta
 receiver-type protocol
 source-address 10.4.255.1
 stream native
 update-policy periodic 90000
 receiver name DNAC_ASSURANCE_RECEIVER
telemetry receiver protocol DNAC_ASSURANCE_RECEIVER
 host ip-address 10.2.254.11 25103
 protocol tls-native profile sdn-network-infra-iwan
telemetry transform trustSecCounterDelta
 input table cts_rolebased_policy
  field dst_sgt
  field src_sgt
  field sgacl_name
  field monitor_mode
  field num_of_sgacl
  field policy_life_time
  field total_deny_count
  field last_updated_time
  field total_permit_count
  join-key cts_role_based_policy_key
  logical-op and
  type mandatory
  uri /services;serviceName=ios_emul_oper/cts_rolebased_policy
 operation 1
  output-field 1
   field cts_rolebased_policy.src_sgt
  output-field 2
   field cts_rolebased_policy.dst_sgt
  output-field 3
   field cts_rolebased_policy.total_permit_count
   output-op type delta
  output-field 4
   field cts_rolebased_policy.total_deny_count
   output-op type delta
  output-field 5
   field cts_rolebased_policy.sgacl_name
  output-field 6
   field cts_rolebased_policy.monitor_mode
  output-field 7
   field cts_rolebased_policy.num_of_sgacl
  output-field 8
   field cts_rolebased_policy.policy_life_time
  output-field 9
   field cts_rolebased_policy.last_updated_time
 specified
netconf-yang
end

SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
SW400#
这张图其实不是 17 个完全独立的实验，而是一套 **Cisco DNAC / Catalyst Center + SD-Access 从“设备纳管 → Fabric 建立 → Overlay 通信 → 微分段 → 宏分段 → Border/Fusion 出口”** 的完整实验链。

我建议你把 **3～19 拆成 6 个实验组** 来做，这样逻辑最清楚。Cisco 官方部署流程本身也是 Design → Discover/Provision → Fabric → VN/Anycast Gateway → Host/Policy → Border Handoff 这样的顺序。([Cisco][1])

---

# 一、先看整个实验拓扑

建议实验环境至少这样：

```text
                         ┌──────────────┐
                         │     ISE      │
                         │802.1X / SGT  │
                         └──────┬───────┘
                                │
                         ┌──────┴───────┐
                         │ DNAC /       │
                         │ Catalyst Ctr │
                         └──────────────┘


                         Underlay IP
                            │
                   ┌────────┴────────┐
                   │ Border + CP     │
                   │  Border/Control │
                   └───────┬─────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
       ┌─────┴─────┐               ┌─────┴─────┐
       │ Fabric    │               │ Fabric    │
       │ Edge 1    │               │ Edge 2    │
       └─────┬─────┘               └─────┬─────┘
             │                           │
           PC-A                         PC-B


Border
  │
  │ VRF-Lite + BGP
  │
Fusion Router
  │
外部网络 / Shared Services
```

做 13、14、16 这些 VXLAN/移动性实验时，**最好一定准备两个 Fabric Edge**。如果两个 PC 都插在同一台 Edge 上，有些流量根本不会经过 Fabric Overlay，你就看不到真正想验证的 VXLAN/LISP 行为。

---

# 实验一：DNAC 基础纳管

对应图片：

```text
3. 配置 Pool
4. Discover Devices
5. Assign Devices to Site
6. Provision Devices
```

## 3. 配置 Pool

### 实验目的

告诉 Catalyst Center：

> 我的网络有哪些 IP 地址段，这些 IP 地址段以后要给哪些站点、用户、AP、Fabric、L3 Handoff 使用。

Catalyst Center 的 IPAM 里通常先创建 **Global Pool**，然后从 Global Pool 中为具体 Site Reserve 一个子网。Cisco 官方也明确说明，SD-Access 的 IP Pool 可用于客户端、AP、Extended Node、LAN Automation 和 Border L3 Handoff 等。([Cisco][1])

例如：

```text
Global Pool
10.4.0.0/16

        ↓ Reserve

IT Pool
10.4.10.0/24
Gateway: 10.4.10.1

Sales Pool
10.4.20.0/24
Gateway: 10.4.20.1
```

注意，这里的 Pool 不只是“DHCP Server 的 DHCP Pool”。

它首先是：

```text
Catalyst Center 的 IP 地址规划/IPAM
```

之后可以关联 DHCP Server，让终端真正通过 DHCP 获取 IP。

### 基本过程

```text
Design
 ↓
Network Settings
 ↓
IP Address Pools
 ↓
Global
 ↓
Add IP Pool
```

例如：

```text
10.4.0.0/16
```

然后到具体 Site：

```text
Global
└─ China
   └─ Shanghai
      └─ Building1
```

Reserve：

```text
10.4.10.0/24  IT
10.4.20.0/24  Sales
```

---

# 4. Discover Devices

## 实验目的

让 DNAC 找到交换机/路由器，并把设备加入 Inventory。

例如：

```text
DNAC
  │
  ├── C9500 Border
  ├── C9300 Edge1
  └── C9300 Edge2
```

Discovery 前最重要的是：

```text
DNAC
 ↓
必须能 IP 到达设备

并且有：
SSH / CLI Credentials
SNMP
NETCONF
```

Cisco 官方部署文档明确要求 Catalyst Center 对设备具有 IP 可达性和 CLI 凭据；发现后设备才会进入 Inventory，并供后续 Provision 使用。([Cisco][1])

### 实验过程

先在交换机保证：

```text
Management / Loopback IP
SSH
SNMP
NETCONF
```

例如：

```text
Edge1 10.4.255.11
Edge2 10.4.255.12
Border 10.4.255.1
```

然后 DNAC：

```text
Provision
 ↓
Inventory
 ↓
Discovery
 ↓
New Discovery
```

输入：

```text
IP Range
10.4.255.1 - 10.4.255.20
```

Discovery 成功以后：

```text
Inventory

Border     Managed
Edge1      Managed
Edge2      Managed
```

---

# 5. Assign Devices to Site

Discovery 只是：

> 我知道这台交换机存在。

但是 DNAC 还不知道：

> 它在哪栋楼、哪个 Floor。

所以要：

```text
Edge1
  ↓
Building1 / Floor1

Edge2
  ↓
Building1 / Floor1

Border
  ↓
Building1
```

### 实验目的

因为很多 DNAC 配置都是：

```text
Site-Based
```

例如：

```text
AAA
DHCP
DNS
NTP
SNMP
IP Pool
Fabric
```

所以必须先知道设备属于哪个 Site。

---

# 6. Provision Devices

这个非常容易和 **Add to Fabric** 混淆。

Provision Device ≠ 建立 SDA Fabric。

Provision 更像：

> 把这个 Site 的基础网络配置真正下发到设备。

例如：

```text
Site
 ├─ AAA
 ├─ DNS
 ├─ DHCP
 ├─ NTP
 ├─ SNMP
 └─ Telemetry
        ↓
     Provision
        ↓
    Catalyst 9300
```

所以你可以理解：

```text
Discover
   ↓
“DNAC认识设备”

Assign Site
   ↓
“DNAC知道设备在哪里”

Provision
   ↓
“DNAC开始管理和配置设备”

Add Fabric Role
   ↓
“设备真正成为SDA节点”
```

---

# 实验二：ISE + VN + SGT

对应：

```text
7. DNAC与ISE集成
8. 创建Virtual Networks
9. 创建Scalable Group Tags
```

这是理解 SDA 最关键的一组。

SD-Access 实际上有两层分段：

```text
第一层
VN / VRF
= Macro Segmentation
= 宏分段

第二层
SGT
= Micro Segmentation
= 微分段
```

Cisco 官方也是这样定义：VN/VRF 做宏分段，SGT/SGACL 做 VN 内部的微分段。([Cisco][2])

---

# 7. DNAC 与 ISE 集成

## 实验目的

为了后面做：

```text
802.1X
MAB
身份认证
SGT
SGACL
Micro Segmentation
```

ISE 是 SDA 身份和策略体系的核心组件。

Cisco 官方说明，ISE 可以动态把用户/设备映射到 Scalable Group，Catalyst Center 用于管理这些组和策略；如果你**只做 VN 宏分段**，ISE 并不是强制的。([Cisco][1])

所以：

```text
只做：

IT_VN
Sales_VN

不需要 ISE 也可以。
```

但是如果要：

```text
员工
服务器
打印机

然后：

员工 → 服务器 Allow
员工 → 打印机 Allow
Guest → 服务器 Deny
```

SGT/SGACL 就需要 ISE 体系。

---

## 实验过程

大体：

```text
Catalyst Center
       │
       │ Integration
       ↓
      ISE
```

然后配置：

```text
AAA
RADIUS
802.1X
```

最终流程：

```text
PC
 │
 │ EAPOL
 ↓
Fabric Edge
 │
 │ RADIUS
 ↓
ISE
 │
 │ Authorization
 ↓
SGT = Employees
 │
 ↓
Fabric Edge
```

于是：

```text
PC-A

IP = 10.4.10.10
VN = IT_VN
SGT = Employee
```

不只是“这个 IP 是谁”，而是：

> 这个设备属于 Employee 这个身份组。

Cisco Catalyst Center 与 ISE 集成还可以通过集中工作流下发 IBNS 2.0、802.1X/MAB、AAA 和 RADIUS 配置到 Fabric Edge。([Cisco][3])

---

# 8. 创建 Virtual Networks

这里开始做：

# Macro Segmentation 宏分段

例如建立：

```text
IT_VN

Sales_VN
```

你可以直接把：

```text
VN ≈ VRF
```

理解成传统网络：

```text
vrf definition IT_VN

vrf definition Sales_VN
```

Cisco 官方定义中，SD-Access 的用户 VN 会被实现为独立的 VRF/转发表。([Cisco][2])

所以：

```text
IT_VN
Routing Table A

Sales_VN
Routing Table B
```

默认：

```text
IT_VN  ✕  Sales_VN
```

不能互相访问。

这就是为什么第 19 步需要 Fusion。

---

# 9. 创建 Scalable Group Tags

这一步就是：

# Micro Segmentation 微分段

例如：

```text
IT_VN
 │
 ├─ Employee    SGT 10
 ├─ Server      SGT 20
 └─ Printer     SGT 30
```

然后创建 Policy：

```text
Source         Destination     Policy

Employee   →   Server          Permit

Employee   →   Printer         Permit

Printer    →   Server          Deny
```

注意：

```text
VN
```

解决的是：

> 大网络之间隔离。

而：

```text
SGT
```

解决的是：

> 同一个 VN 里面不同人/设备之间怎么办。

这是非常重要的区别。([Cisco][3])

---

# 实验三：建立真正的 SDA Fabric

对应：

```text
10. 创建Fabric Site
11. 将设备加入Fabric并分配角色
12. Host Onboarding
```

---

# 10. 创建 Fabric Site

前面：

```text
Site
```

只是地理层次。

现在：

```text
Fabric Site
```

意味着：

> 我要在这个 Site 上运行 SDA Overlay。

可以理解成：

```text
普通 Site

Building1
     ↓

Enable Fabric
     ↓

SDA Fabric Site
```

---

# 11. 加入 Fabric 并配置角色

这一步是 SDA 的核心。

主要三个角色：

```text
Control Plane Node
Border Node
Fabric Edge Node
```

---

## Control Plane

负责：

```text
Endpoint → Location
```

映射。

例如：

```text
10.4.10.100
     ↓
Edge1
RLOC = 10.4.255.11
```

换到 Edge2：

```text
10.4.10.100
     ↓
Edge2
RLOC = 10.4.255.12
```

这里主要使用：

```text
LISP
```

---

# Fabric Edge

终端直接连接这里：

```text
PC
 ↓
Fabric Edge
```

负责：

```text
Host onboarding
Anycast Gateway
VXLAN encapsulation
SGT
Policy enforcement
LISP registration
```

Cisco 对 Fabric Edge 的定义也是连接用户/IoT Endpoint、获取其访问属性并执行相应策略的 Fabric 节点。([Cisco][2])

---

# Border

负责：

```text
SDA Fabric
     ↓
外部传统网络
```

例如：

```text
SDA
 │
Border
 │
Fusion
 │
Core
 │
Internet
```

---

## 推荐实验分配

实验环境可以：

```text
C9500
Border + Control Plane

C9300-1
Fabric Edge

C9300-2
Fabric Edge
```

这样既省设备，又能做后面的：

```text
VXLAN
Host Mobility
Anycast Gateway
```

---

# 12. Host Onboarding

这一项的目标是：

> 真正让 PC 进入 SDA Fabric。

例如 PC 接：

```text
Edge1 Gi1/0/10
```

端口需要获得相应的：

```text
VN
IP Pool
SGT
Authentication
```

最终：

```text
PC-A
 │
 ↓
Edge1
 │
 ├─ VN = IT_VN
 ├─ Pool = 10.4.10.0/24
 ├─ Gateway = 10.4.10.1
 └─ SGT = Employee
```

PC DHCP：

```text
DHCP Discover
     ↓
Fabric Edge
     ↓
DHCP Relay
     ↓
DHCP Server
```

然后 Edge 学到：

```text
MAC
IP
Interface
SGT
```

并向 LISP Control Plane 注册 Endpoint。

你之前看到的：

```text
ip dhcp relay information option
ip dhcp snooping
```

就是这个过程的一部分；Cisco 官方也专门提供了 Fabric Edge DHCP onboarding 的验证流程。([Cisco][4])

可以检查：

```text
show ip dhcp snooping binding
```

比如：

```text
MAC                IP           VLAN Interface

AAAA.BBBB.CCCC  10.4.10.11      xxx Gi1/0/10
```

---

# 实验四：真正理解 VXLAN / LISP

对应：

```text
13. 同VN同子网通信
14. 同VN不同子网通信
15. Anycast Gateway
16. Host Mobility
```

这四个实验非常重要。

---

# 13. 同 VN + 同子网

例如：

```text
             SDA Fabric

PC-A                           PC-B
10.4.10.11                    10.4.10.12
   │                             │
 Edge1                         Edge2
   │                             │
   └──────── VXLAN ──────────────┘

VN = IT_VN
Subnet = 10.4.10.0/24
```

### 实验目的

验证：

```text
不同 Fabric Edge

同一个：
VN
Subnet

可以跨 Fabric 通信。
```

测试：

```text
PC-A

ping 10.4.10.12
```

应该：

```text
成功
```

数据在 Edge1 和 Edge2 之间通过 Fabric 的 VXLAN 数据平面传送，而 LISP 负责 Endpoint/location 的控制平面信息；Cisco 也有专门的 SDA Layer-2 LISP 验证文档。([Cisco][5])

可以把这里理解为：

```text
LISP
负责：

“10.4.10.12在哪里？”

        ↓

Control Plane：

“在Edge2。”

        ↓

Edge1
VXLAN encapsulation

        ↓

Edge2
```

---

# 14. 同 VN，不同子网

例如：

```text
PC-A
10.4.10.11/24
GW 10.4.10.1
 │
Edge1


       SDA


Edge2
 │
PC-B
10.4.20.11/24
GW 10.4.20.1
```

但是：

```text
10.4.10.0/24
10.4.20.0/24
```

都属于：

```text
IT_VN
```

所以：

```text
同一个 VRF
```

可以路由。

测试：

```text
PC-A

ping 10.4.20.11
```

应该成功。

这里就是 **L3 Overlay / L3 VNID 对应的路由语义**。在 LISP Fabric 中，LISP instance 可以关联 VRF 的 L3 服务，也可以关联 VLAN 的 L2 服务。([Cisco][6])

---

# 15. Anycast Gateway

这个其实是理解第 14 步的关键。

假设：

```text
IT Pool

10.4.10.0/24

Gateway
10.4.10.1
```

在传统网络可能：

```text
Core
interface Vlan10
 ip address 10.4.10.1
```

所有用户都跑去 Core 找网关。

但是 SDA 不是。

---

## SDA

每个 Fabric Edge 都可以拥有：

```text
10.4.10.1
```

于是：

```text
           Gateway
          10.4.10.1

Edge1                     Edge2
10.4.10.1                 10.4.10.1
   │                         │
 PC-A                       PC-B
```

这就是：

# Anycast Gateway

Cisco 的定义就是把 IP Pool 关联到 VN 后形成分布式默认网关，作用类似传统网络中的 first-hop SVI。([Cisco][1])

它不是：

```text
HSRP
VRRP
```

那种：

```text
一个 Active
一个 Standby
```

而是：

```text
Edge1：我是你的网关

Edge2：我也是你的网关
```

所以用户走到哪里：

```text
最近的 Fabric Edge
```

就是他的网关。

---

# 16. Host Mobility

这个实验特别适合理解：

```text
为什么SDA要LISP
```

先：

```text
PC
10.4.10.100

   ↓

Edge1
```

Control Plane：

```text
10.4.10.100
      →
RLOC Edge1
```

然后把网线拔掉：

```text
Edge1
```

插到：

```text
Edge2
```

IP 保持：

```text
10.4.10.100
```

新的注册变成：

```text
10.4.10.100
      →
RLOC Edge2
```

这就是：

```text
EID
10.4.10.100

与

RLOC
设备位置

分离
```

所以：

```text
IP不一定代表位置
```

而 LISP Control Plane 负责告诉网络：

> 这个 Host 现在在哪里。

Anycast Gateway 也让 Endpoint 换到另一台 Edge 时仍然面对相同的 First-Hop Gateway。([Cisco Community][7])

### 实验方法

先：

```text
PC → Edge1
```

确认：

```text
ping GW
ping PC-B
```

然后保持：

```text
IP不变
```

移动：

```text
PC → Edge2
```

再 Ping。

观察：

```text
LISP registration
```

从：

```text
Edge1 RLOC
```

变化到：

```text
Edge2 RLOC
```

---

# 实验五：SGT 微分段

对应：

# 17. SDA 的 SGT 同一 VN 内微观分段

这是前面：

```text
7 ISE

9 Scalable Group
```

真正派上用场。

拓扑：

```text
             IT_VN

PC-A                           PC-B

Employee                       Server
SGT 10                         SGT 20
 │                               │
Edge1                           Edge2
```

然后定义：

```text
Employee → Server
Permit
```

Ping：

```text
成功
```

再改：

```text
Employee → Server
Deny
```

Ping：

```text
失败
```

但是要注意：

```text
IP路由其实是通的
```

阻止通信的不是 VRF。

而是：

```text
SGT + SGACL
```

也就是：

# Micro Segmentation

Cisco 官方的定义就是在同一 VN 内基于 Source Group → Destination Group 做访问控制。([Cisco][2])

例如：

```text
                 IT_VN

Employee         Server          Printer
SGT 10           SGT 20          SGT 30


         Security Matrix

             Server    Printer

Employee     Permit    Permit

Printer      Deny        -
```

这就是为什么图上写：

```text
步骤17需要完成步骤7和步骤9
```

因为：

```text
7 = ISE
9 = SGT

        ↓

才有真正的身份微分段
```

---

# 实验六：Macro Segmentation + Fusion

对应：

```text
18. 单Fabric双VN
19. 双VN通过Border/Fusion互通
```

---

# 18. 单 Fabric 双 VN

建立：

```text
IT_VN

Sales_VN
```

例如：

```text
PC-A
10.4.10.10
IT_VN

        SDA Fabric

PC-B
10.4.20.10
Sales_VN
```

虽然：

```text
都在同一个 SDA Fabric
```

但是：

```text
IT_VN
   ↓
VRF IT

Sales_VN
   ↓
VRF Sales
```

因此默认：

```text
PC-A
 ↓
X
 ↓
PC-B
```

Ping 不通。

这就是：

# Macro Segmentation

Cisco 明确把 VN 定义为利用独立转发表/VRF 实现的宏分段。([Cisco][2])

---

# 19. Border + Fusion 实现不同 VN 通信

这就是前面你问过的：

> Border 为什么要和 BGP 有关系？

现在就完全串起来了。

拓扑：

```text
IT_VN
   │
   │
SDA Fabric
   │
Border
   │
   │ VRF-Lite
   │ + eBGP
   │
Fusion
   │
   ├──── IT VRF
   │
   └──── Sales VRF
```

SDA 内：

```text
IT_VN
      X
Sales_VN
```

不能直接互通。

所以：

```text
IT
 ↓
Border
 ↓
Fusion
 ↓
Route Leaking
 ↓
Border
 ↓
Sales
```

---

## Border 做什么

Border 把：

```text
SDA VN
```

转换/延伸到传统网络的：

```text
VRF
```

例如：

```text
IT_VN
 ↓
VRF IT

Sales_VN
 ↓
VRF Sales
```

Catalyst Center 的 Layer 3 Handoff 可以在 Border 上自动建立基于 VRF-Lite 的接口，并使用 eBGP 向外部路由域发布 Fabric Endpoint 前缀、学习外部路由。([Cisco][1])

---

# Fusion 做什么

Fusion 的核心任务：

# Route Leaking

例如：

```text
VRF IT
10.4.10.0/24

VRF Sales
10.4.20.0/24
```

本来：

```text
IT
 X
Sales
```

Fusion：

```text
VRF IT
   │
   │ Route Leak
   ↓
VRF Sales
```

于是：

```text
10.4.10.0/24
         ↕
10.4.20.0/24
```

Cisco 官方的 Macro Segmentation 指南也是用 Fusion 处理不同 VN/VRF 之间以及 VN 到 Shared Services 的通信。([Cisco][8])

---

# 你这 3～19 步最重要的逻辑关系

可以记成这一条链：

```text
3 IP Pool
   ↓
准备地址

4 Discovery
   ↓
找到设备

5 Assign Site
   ↓
设备归属站点

6 Provision
   ↓
DNAC正式管理设备

7 ISE
   ↓
身份/认证/SGT

8 VN
   ↓
Macro Segmentation

9 SGT
   ↓
Micro Segmentation

10 Fabric Site
   ↓
建立SDA区域

11 Fabric Roles
   ↓
CP / Border / Edge

12 Host Onboarding
   ↓
PC真正进入Fabric

13 同VN同Subnet
   ↓
验证L2 Overlay/VXLAN

14 同VN不同Subnet
   ↓
验证L3 Overlay

15 Anycast Gateway
   ↓
验证分布式网关

16 Host Mobility
   ↓
验证LISP EID→RLOC变化

17 SGT实验
   ↓
验证Micro Segmentation

18 双VN
   ↓
验证Macro Segmentation隔离

19 Border + Fusion
   ↓
验证跨VN / 外部通信
```

## 最值得做的其实是这 7 个核心实验

| 实验              | 你真正要学懂什么          |
| --------------- | ----------------- |
| Host Onboarding | Endpoint 怎么进入 SDA |
| 同 VN 同网段        | LISP + VXLAN L2   |
| 同 VN 不同网段       | VXLAN L3 + VRF    |
| Anycast Gateway | 为什么每个 Edge 都能当网关  |
| Host Mobility   | LISP 为什么存在        |
| SGT Microseg    | 同一 VN 内怎么隔离       |
| VN + Fusion     | 不同 VRF/VN 怎么通信    |

如果你现在已经把 **DNAC Discovery / Provision / Fabric Role** 配得差不多了，我建议下一步不要继续泛泛看概念，直接从 **实验 13：两台 Fabric Edge + 两台 PC 的“同 VN 同网段 VXLAN 实验”** 开始。这个实验做通以后，我可以继续按你的实际 `10.4.10.0/24、10.4.20.0/24、NJQYT_IT_VN` 配置，给你写出 **具体拓扑、DNAC 点哪里、PC 配什么 IP、交换机用哪些 `show lisp` / `show vxlan` 命令、正常输出应该看到什么**。

[1]: https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/cisco-validated-solution-profiles/validated-profile-sda-deployment.html "SD-Access Deployment Using Cisco Catalyst Center - Cisco"
[2]: https://www.cisco.com/c/en/us/solutions/collateral/enterprise-networks/software-defined-access/nb-09-sda-faq-cte-en.html "Cisco Software-Defined Access FAQ - Cisco"
[3]: https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-sda-design-guide.html "Design Zone - Software-Defined Access - Cisco"
[4]: https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/dna-center/tech_notes/sda_dhcp/b_cisco_sda_dhcp.html?utm_source=chatgpt.com "Cisco SD-Access Fabric Edge DHCP Process/Packet Flow ..."
[5]: https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9300-series-switches/220515-verify-layer-2-lisp-connectivity-in-sda.html?utm_source=chatgpt.com "Verify Layer 2 LISP Connectivity in SDA on Catalyst 9000 ..."
[6]: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lisp_vxlan/b-179-lisp-vxlan-fabric-cg/configure-control-plane-lisp-vxlan.html?utm_source=chatgpt.com "LISP VXLAN Fabric Configuration Guide, Cisco IOS XE ..."
[7]: https://community.cisco.com/t5/networking-knowledge-base/layer-2-virtual-networks-with-gateway-outside-of-fabric/ta-p/4835888?utm_source=chatgpt.com "Layer 2 Virtual Networks with Gateway Outside of Fabric"
[8]: https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-sda-macro-segmentation-deploy-guide.html "Design Zone - Software-Defined Access Macro Segmentation Deployment Guide - Cisco"



根据您提供的两张图片内容，我已将其中所有文字提取并整理如下。第一张图片为网络配置（ESI/VXLAN 部分），第二张为 LISP 协议配置与拓扑说明。提取结果如下：

---

### 第一张图片内容（ESI 与 VXLAN 配置）：

```
//创建一个ESI实例1 说人话就是VRF是一个虚拟的路由器，有自己独立的路由表
但是VXLAN可以理解为是2层交换网络的扩展，所以ESI则是一个虚拟的交换机，有自己独立的MAC表。
//该ESI虚拟交换机收到的是没有VLAN Tag标记的原始数据帧
bridge-domain 1
  member GigabitEthernet2 service-instance 1
  exit
  member vni 10000
//创建BD桥接域1，BD域则像是胶水粘合剂，把传统的2层数据包粘贴上VXLAN的头部
//将G2接口下ESI1虚拟交换机收到的数据包，重装封装到VNI10000，然后送入到VXLAN隧道

CSR2
interface vnel
  no ip address
  source-interface Loopback0
  member vni 10000
  ingress-replication 1.1.1.1
interface GigabitEthernet2
  no shutdown
  service instance 1 ethernet
    encapsulation untagged
    exit
bridge-domain 1
  member GigabitEthernet2 service-instance 1
  exit
  member vni 10000

interface vnel
  no ip address
  source-interface Loopback0
  member vni 10000
  ingress-replication 2.2.2.2
interface GigabitEthernet2
  no shutdown
  service instance 1 ethernet
    encapsulation untagged
    exit
bridge-domain 1
  member GigabitEthernet2 service-instance 1
  exit
  member vni 10000
```

---

### 第二张图片内容（LISP 配置与拓扑说明）：

```
EID1.1.1.1/32

拓扑描述

R3-R4-R5运行OSPF协议

EID11.11.11.11/32

R1-R3,R2-R5运行EIGRP协议

R4为LISPMap-server映射服务器和map-resolver映射解析服务器

无标题-记事本

router lisp

文件（F）编辑（E）格式（O）查看（V)帮助（H）

database-mapping 1.1.1.1/3234.1.1.3priority100weight100

R4#showlisp session

ipv4itrmap-resolver4.4.4.4

//查看LISP会话，分别和R3和R5建立了LISP会话

ipv4itr

Sessions for VRF default, total: 2, established: 2

ipv4etrmap-server4.4.4.4key1234

Peer

State

Up/Down

In/Out

Users

ipv4etr

34.1.1.3

Up

00:18:23

1/3

1

exit

45.1.1.5

Up

00:18:17

1/3

1

//这几条命令的意思就是告诉MR映射解析服务器。通过自己34.1.1.3这个RL0C（路由器）-可以访问1.1.1.1/

//第二个命令的意思就是如果有不知道的主机地址信息。要去问MS映射服务器4.4.4.4，主机的位置在哪里

R4#showlisp site

//查看LISP的站点注册信息

//本设备即是LISP隧道的入口，也是LISP隧道的出口，入口要进行LISP的封装，出口要解LISP的封装

R5

LISP Site Registration Information

router lisp

*=Some locators are down or unreachable

database-mapping 2.2.2.2/3245.1.1.5 priority 100 weight 100

#= Some registrations are sourced by reliable transport

ipv4 itrmap-resolver 4.4.4.4

Site Name

Last

Up

Who Last

Inst

EID Prefix

ipv4itr

Register

Registered

ID

ipv4etrmap-server4.4.4.4key1234

1

00:00:06

yes

34.1.1.3

1.1.ipv4 etr

2

00:00:00

yes

45.1.1.5

2.2.exit

//可以看到从两个站点分别注册上来了EID前缀信息（路由）。人话就是通过34.1.1.3
//至于怎么到34.1.1.3或者45.1.1.5底层的IGPOSPF协议来选路

R4 MS/MR

R3#show ip lisp mao-cache

ipv4 map-server

//在R3查看lisp的缓存消息，默认情况下任何路由都需要往MS服务器4.4.4.4进行请求角ipv4map-resolver

LISP IPv4 Mapping Cache for EID-table default (IID 0),1 entries

site1

0.0.0.0/0,uptime:00:17:02,expires:never,via static send map-request

authentication-key 1234

Negative cache entry, action: send-map-request

eid-prefix 1.1.1.1/32

exit

R3/R5

site2

interface Etherneto/2

authentication-key 1234

ip summary-address eigrp 900.0.0.0 0.0.0.0

eid-prefix 2.2.2.2/32

//R3和R5分别给R1和R2产生一条默认路由

exit

R1#ping 2.2.2.2 source 1.1.1.1

I

//IP是MS映射服务器，接受站点的映射注册信息，

Type escape sequence to abort.

//又是MR映射解析服务器，用于解析主机所在的站点位置

Sending 5,100-byte ICMP Echos to 2.2.2.2, timeout is 2 seconds:

Packet sent with a source address of 1.1.1.1

!!!!

//R1上使用源地址1.1.1.1测试业务连通性，成功

原理此地就是R3向MS映射服务器发送了LISP的封装映射请求消息。说我是34.1.1.3
映MS映射服务器会将查找自已对的站点记录，会将该封装请求报文发给站点2的R5，R5
```

---

如果还需要进一步整理为表格、拓扑说明或配置对比，也可以告诉我。
