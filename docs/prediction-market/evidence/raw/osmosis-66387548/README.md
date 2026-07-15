# Osmosis height 66,387,548 raw evidence

**Chain ID:** `osmosis-1`  
**Block time:** 2026-07-15T16:45:07.107892122Z  
**Capture date:** 2026-07-15  
**Request header:** `x-cosmos-block-height: 66387548`

The two public gateways were `https://lcd.osmosis.zone` and `https://osmosis-api.polkachu.com`. Every envelope returned `grpc-metadata-x-cosmos-block-height: 66387548`; the decoded bodies agree byte-for-byte between providers.

Each `*.http.b64` file base64-encodes the exact HTTP status line, CRLF-delimited response headers, blank separator, and full JSON body received from `curl -D -`. Decode with `base64 -d FILE`; extract the body with `base64 -d FILE | sed '1,/^\\r$/d'`.

## Requests

| File | Path |
| --- | --- |
| `block` | `/cosmos/base/tendermint/v1beta1/blocks/66387548` |
| `pool-497` | `/osmosis/poolmanager/v1beta1/pools/497` |
| `pool-498` | `/osmosis/poolmanager/v1beta1/pools/498` |
| `pool-498-twap-24h` | Arithmetic TWAP for JUNO/ATOM pool 498 from 2026-07-14T16:28:23Z through 2026-07-15T16:28:23Z |

## Integrity manifest

| Envelope | Decoded bytes | Envelope SHA-256 | Body SHA-256 |
| --- | ---: | --- | --- |
| `lcd-osmosis-zone/block.http.b64` | 36232 | `8410a50237a4bf776dd43cef5e1581ebfead80568412267d892a8fcabd39517a` | `280f40716657dc06f53817b610fbb608a699b00173ed0e7ac0492426c649a011` |
| `lcd-osmosis-zone/pool-497.http.b64` | 874 | `295c9d8c7a0c6c890c74c32a1c63040bbf22b87f97c352dbde3e3ac6b25bad8a` | `dc79e9eb4f538cc7e7c7e15c54d38264d0fe94aa9564307c6d21949e678c3014` |
| `lcd-osmosis-zone/pool-498-twap-24h.http.b64` | 288 | `faaa2172cf1606a42ab06db633a1d77a9c214c908538314183646198e6762551` | `26c697ca96e7862be61c32e42a511bc59e1af5dfbc031ca8c8f8e029892782dc` |
| `lcd-osmosis-zone/pool-498.http.b64` | 934 | `9488186e16328d50bb34c1a7ad86820ef03d22acf39c03cb8e2c7eb97fe728c4` | `03d3caf4f0bd075b2668e5344f7b54ee151ab56cc4eca7bc344bae0cc78a3c2d` |
| `polkachu/block.http.b64` | 36649 | `35d1ba3d50ea011fcc0398aee12484ab8b0908b02e5cd6049777e759e13ebf39` | `280f40716657dc06f53817b610fbb608a699b00173ed0e7ac0492426c649a011` |
| `polkachu/pool-497.http.b64` | 1287 | `eb78b1fb34214880a005d9d0170ee0fd5e89326cb6c3fcfcc06a23213a09fd0f` | `dc79e9eb4f538cc7e7c7e15c54d38264d0fe94aa9564307c6d21949e678c3014` |
| `polkachu/pool-498-twap-24h.http.b64` | 701 | `f46218b477399c56b9d93f8d8a9b3d37a437d33df074300bd6ec9440d55c7ed2` | `26c697ca96e7862be61c32e42a511bc59e1af5dfbc031ca8c8f8e029892782dc` |
| `polkachu/pool-498.http.b64` | 1353 | `9f3e54e87c8d4a8d71f9916dc28fd745c983512f55e5d0d05b1f8130ee302e82` | `03d3caf4f0bd075b2668e5344f7b54ee151ab56cc4eca7bc344bae0cc78a3c2d` |

