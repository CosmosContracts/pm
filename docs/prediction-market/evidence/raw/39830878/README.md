# Juno height 39,830,878 raw evidence

**Chain ID:** `juno-1`  
**Block time:** 2026-07-15T16:28:23.815568018Z  
**Capture date:** 2026-07-15  
**Request header:** `x-cosmos-block-height: 39830878`

## Providers

- `cosmos-directory`: `https://rest.cosmos.directory/juno`
- `polkachu`: `https://juno-api.polkachu.com`

These are separately operated public gateways. Every saved response reports `grpc-metadata-x-cosmos-block-height: 39830878`. Provider independence here detects gateway disagreement; it is not a light-client proof and does not replace a sign-off refresh.

## Representation

For each request:

- `*.http.b64` is the normative byte-preserving envelope. Base64 decoding recovers the HTTP status line, CRLF-delimited response headers, the blank separator, and the complete JSON body exactly as `curl -D -` received them.
- `*.http` is an earlier human-readable capture of the same height and endpoint. Its CRLF line endings were normalized to LF for review, so it is not the byte-preserving representation.
- The response bodies from both providers are byte-identical for all archived endpoints except `node-info`. That exception is expected because node identity and connection data describe each provider's node; both node responses report Juno `v29.1.0`, Cosmos SDK `v0.50.13`, wasmd `v0.54.0`, wasmvm `v2.2.4`, and app commit `9e38daa020a69ce64127db92aef861d8b69d3d81`.

Decode one envelope:

```sh
base64 -d cosmos-directory/oracle-code-info.http.b64
```

Extract only its body:

```sh
base64 -d cosmos-directory/oracle-code-info.http.b64 | sed '1,/^\r$/d'
```

## Request set

| File stem | Request path |
| --- | --- |
| `block` | `/cosmos/base/tendermint/v1beta1/blocks/39830878` |
| `node-info` | `/cosmos/base/tendermint/v1beta1/node_info` |
| `gov-deposit-params` | `/cosmos/gov/v1/params/deposit` |
| `gov-voting-params` | `/cosmos/gov/v1/params/voting` |
| `consensus-params` | `/cosmos/consensus/v1/params` |
| `wasm-access-params` | `/cosmwasm/wasm/v1/codes/params` |
| `module-accounts` | `/cosmos/auth/v1beta1/module_accounts` |
| `staking-pool` | `/cosmos/staking/v1beta1/pool` |
| `ujuno-supply` | `/cosmos/bank/v1beta1/supply/by_denom?denom=ujuno` |
| `bonded-validators` | `/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED&pagination.limit=200` |
| `oracle-contract` | `/cosmwasm/wasm/v1/contract/juno1g0pveeymzn3a3asu6v2dhkclqhwsndmvjugjx8a4qx554esp5yessuceur` |
| `oracle-code-info` | `/cosmwasm/wasm/v1/code-info/5121` |
| `oracle-config` | `/cosmwasm/wasm/v1/contract/juno1g0pveeymzn3a3asu6v2dhkclqhwsndmvjugjx8a4qx554esp5yessuceur/smart/eyJjb25maWciOnt9fQ==` |
| `gov-proposal-N` | `/cosmos/gov/v1/proposals/N`, for N = 357, 363, and 371–375 |

## Integrity manifest

The envelope hash covers the decoded status line, headers, CRLF separator, and body. The body hash covers exactly the bytes after the first CRLF-blank line.

| Envelope | Decoded bytes | Envelope SHA-256 | Body SHA-256 |
| --- | ---: | --- | --- |
| `cosmos-directory/block.http.b64` | 14862 | `ff62d99e559165c03e644adc8b3a32fe8139bea840b0d754f2b7c94031f63f36` | `0bdaaab9025f9bf153e88abe1673819d8de1767c1fd22882fb5408af1a662db7` |
| `cosmos-directory/bonded-validators.http.b64` | 24471 | `28e448fca21d0f43b83246ccd9c1dd1a7f1038e0a235fe253a7e2ac003566dfe` | `42fafdb55c699b033d224919414c9a3668fec4e75b543d0446328aa6058d8ee3` |
| `cosmos-directory/gov-deposit-params.http.b64` | 1493 | `d948ec70dc100f0bf25005a7f54824bbf0ec7b027efbaf078774f89eb8bf0301` | `3a362eb4fe0d1f66af3bd74a5e45e56f5c9470659a9ab6a8f14e6fed69da23d9` |
| `cosmos-directory/gov-proposal-357.http.b64` | 2696 | `a716c60293dc59d25e1ba28846ed6e6c92ac8875d26ad2c57024386ace8f0454` | `1476b443fb930666088ef17d68e120a1d891850231e99622e096722d48981e98` |
| `cosmos-directory/gov-proposal-363.http.b64` | 3118 | `daff43b128ffea8e69ac13bfd18b74a627d99ea8e9ac9dcaab274848c7d6ba4a` | `ccef790caf9f85c66beeae19a1c4418c8294717c94636f9a88de47e96b6722ce` |
| `cosmos-directory/gov-proposal-371.http.b64` | 3929 | `a01400fe229e943d93aff1a02a0ffee37b6f9f23476579ef356a74dc3d2f7350` | `28c818cbbb2b2b5f9a44261378beae437a2bc67da3ea0b6a2c29341454e33ba0` |
| `cosmos-directory/gov-proposal-372.http.b64` | 3271 | `b80c8414d31460bfbdb80b3633d68376e10b29f1f8cfce2add1c78f281da7429` | `39d7a8838321e75b30c1a8dfd3b39a0e64c2b529d9a690b7e9f23a5b397e245f` |
| `cosmos-directory/gov-proposal-373.http.b64` | 3973 | `e7fffb46072a28fa82ea0ef91e06d61a232cf058e867607f0b4d57fffdd7a95c` | `ed4a63d826be5bf525f8d20be679f0725b872c1f306e2225beacbfc58cd2a85f` |
| `cosmos-directory/gov-proposal-374.http.b64` | 12782 | `c1dee3415f04a7edfcf22110206813fee07d7b87aa3bec076ebc74204a22bb12` | `45220d2b8d6cd56bf88d050fb5235f30e20f8f78845fb9c4e644a616017886a7` |
| `cosmos-directory/gov-proposal-375.http.b64` | 2946 | `b29953f9f42f49a4b1eb91a44756c5e5f2f5016b432a5e0017cac96a10b640d2` | `8b55c93218c57bf4b7bbd9000591906b97c6c1125c8071858644ab8956439425` |
| `cosmos-directory/gov-voting-params.http.b64` | 1474 | `fc19d5f87eb54a15943615cbbdcb3511daae302c440b69e55608246ae3036a94` | `d61e86c014ede66a03657846c0594b0dd3adf2139c5224af648fa304badcba69` |
| `cosmos-directory/module-accounts.http.b64` | 4216 | `13c6064a8694a120108c995067943d1aaba4f7a21ed27a9d7d4f8ddb8f96cad0` | `207574be3ccd1500fd4d3257422ccf41dee187c496d0c4e26b2f84fab5697b0b` |
| `cosmos-directory/node-info.http.b64` | 25442 | `39ca2d328420520ac08feb56a7066606ec47ab2a6fe50b105668149f3b3632df` | `2362964c2ff214690d920ffee46e91e21b69da816091f576e8363c9de5f5df5c` |
| `cosmos-directory/oracle-code-info.http.b64` | 974 | `f1731e42ff97eb5842b671017a7bdae35d5073ad77188e02e73bfcbb14e8fcc3` | `d3edf4e6049370b01fc10e43cf1ba9fa84e2e35dce511a7b06e76209d145f95f` |
| `cosmos-directory/oracle-config.http.b64` | 897 | `1f6aff17066bb11e03f0717a23bdd37fff0c89dba5b9d57c82db1e680d06b6fb` | `58935555876c102b785b2ab5b87ad0f388458b7373095c016f62a39c230da51f` |
| `cosmos-directory/oracle-contract.http.b64` | 1122 | `5fae2ec0de415e5d5affcef7ee5941418ff21734e51f1d33ef3328428c262979` | `6ba15ce06e68d9abb2779e9a9e564dbb4adc9d6b0f5bd4607f83bf6543bbf55e` |
| `cosmos-directory/staking-pool.http.b64` | 792 | `6a40869be43185bb85d1614330677651e6f0377031452afb1cf20c16dd80ab17` | `21cb246305b20bef706a592a221eb77f609724e4b49b7a31f4a176457197fcdd` |
| `cosmos-directory/ujuno-supply.http.b64` | 814 | `58d3107f5c68a2419c30fe98b75bc393eae2024bcc1a3f0c80425ac3a133e9b5` | `39a8693c9c9bf3de95c6ed90868dd91f0014cd3f5b9c04e595533074df883dd9` |
| `polkachu/block.http.b64` | 14789 | `87af5a38dc0026ca8bd9ddce89066689ed7d9f564c4b12b65b02e09920c3688d` | `0bdaaab9025f9bf153e88abe1673819d8de1767c1fd22882fb5408af1a662db7` |
| `polkachu/bonded-validators.http.b64` | 24412 | `4538c15388cd167e6287d9863427d64ad198521dc084aafd382e556cac3510e2` | `42fafdb55c699b033d224919414c9a3668fec4e75b543d0446328aa6058d8ee3` |
| `polkachu/gov-deposit-params.http.b64` | 1432 | `4b6b81ca7cc715913fee12b73fb79c9de3903b318578182b1aaa116cde024ad7` | `3a362eb4fe0d1f66af3bd74a5e45e56f5c9470659a9ab6a8f14e6fed69da23d9` |
| `polkachu/gov-proposal-357.http.b64` | 2580 | `5bc08451622be0afe0c0039d99cd02213e8cf15a4fe03bbc9d0cd164228026c4` | `1476b443fb930666088ef17d68e120a1d891850231e99622e096722d48981e98` |
| `polkachu/gov-proposal-363.http.b64` | 3053 | `85a5de429bfaae6140e4ba16503715a10e5d1b5840d0c34c2a311c8477fec5c8` | `ccef790caf9f85c66beeae19a1c4418c8294717c94636f9a88de47e96b6722ce` |
| `polkachu/gov-proposal-371.http.b64` | 3872 | `7910d792dc70a4726f1bc2b953cdfe2e6887b199081f1359e315a1c06144b416` | `28c818cbbb2b2b5f9a44261378beae437a2bc67da3ea0b6a2c29341454e33ba0` |
| `polkachu/gov-proposal-372.http.b64` | 3204 | `57ff58ffa28efbdf9fd78061a37743fd48a915dab49bb0da884f48396d4c255c` | `39d7a8838321e75b30c1a8dfd3b39a0e64c2b529d9a690b7e9f23a5b397e245f` |
| `polkachu/gov-proposal-373.http.b64` | 3906 | `fdaba93f90c1854b71d300d27218438c91076df0e13b81a95b05bbbdc6d21d1f` | `ed4a63d826be5bf525f8d20be679f0725b872c1f306e2225beacbfc58cd2a85f` |
| `polkachu/gov-proposal-374.http.b64` | 12715 | `5438336ee6cbbd859e0bdc67367f625a3a4a8c2735259ce4aad9666ec14870c3` | `45220d2b8d6cd56bf88d050fb5235f30e20f8f78845fb9c4e644a616017886a7` |
| `polkachu/gov-proposal-375.http.b64` | 2883 | `2b8b86233fa3b68ce60f935792fb8663290790776d350b8d032cf8aed599ea5c` | `8b55c93218c57bf4b7bbd9000591906b97c6c1125c8071858644ab8956439425` |
| `polkachu/gov-voting-params.http.b64` | 1375 | `a7d04cc884f7e9c013dbd1df06a461c3e169a70b1f43cda2129646470516eb3d` | `d61e86c014ede66a03657846c0594b0dd3adf2139c5224af648fa304badcba69` |
| `polkachu/module-accounts.http.b64` | 4151 | `f1dbc53cf13295bdd612d73a50e71a924503c2ac434811d2f01f657bd4692c23` | `207574be3ccd1500fd4d3257422ccf41dee187c496d0c4e26b2f84fab5697b0b` |
| `polkachu/node-info.http.b64` | 25391 | `d4f315890cf2e45aa8a0b445d9c62aab4973a616384d25ba3110724bb0e126de` | `2ab3c42f8b8f2206f5d20032e50a336b9cc48a43b53ea7ab39b2aae08d6b3223` |
| `polkachu/oracle-code-info.http.b64` | 875 | `19784722e07ef2f2799c4146e6d4a445c58f84ddde1d3a6d9fe6d95abede91f7` | `d3edf4e6049370b01fc10e43cf1ba9fa84e2e35dce511a7b06e76209d145f95f` |
| `polkachu/oracle-config.http.b64` | 790 | `35319420298781e67dc753ff2b45ee396b79ba687f0ec97dc9ef29b39adf8813` | `58935555876c102b785b2ab5b87ad0f388458b7373095c016f62a39c230da51f` |
| `polkachu/oracle-contract.http.b64` | 1019 | `4b154ac32120eda41c31aaf2f8f16a8ca7465af9f54d29c0970d6e5221c6c81e` | `6ba15ce06e68d9abb2779e9a9e564dbb4adc9d6b0f5bd4607f83bf6543bbf55e` |
| `polkachu/staking-pool.http.b64` | 741 | `9d28e4f69517b80841c0af1ac3941b64b07031e2a54cbf68027a4a73029e33b8` | `21cb246305b20bef706a592a221eb77f609724e4b49b7a31f4a176457197fcdd` |
| `polkachu/ujuno-supply.http.b64` | 712 | `b8ed3b2b819ad1626a1692b791e0a64573344aeab155218b9292c03286631ad0` | `39a8693c9c9bf3de95c6ed90868dd91f0014cd3f5b9c04e595533074df883dd9` |
| `cosmos-directory/consensus-params.http.b64` | 1001 | `a8a769cb66619f65a92c414a2ef349d247f7435e1a76607c7f903e8bd5a05edd` | `3495288ea94824d1d77de46e094800d00b9ef1b8976d5700bc37ff19b56dd780` |
| `polkachu/consensus-params.http.b64` | 888 | `07f070c800a7818d08bdf00cee676467cf55cbbc830c8a5b8a6d4f10d12bb94f` | `3495288ea94824d1d77de46e094800d00b9ef1b8976d5700bc37ff19b56dd780` |
| `cosmos-directory/wasm-access-params.http.b64` | 885 | `289284bd231007886c91a23ba6ed323b2f3a9adfcde228af59562263568fb8b1` | `ea483af6fc50cbb29a36ef194bb172a9a4d6793862c72a6e64f8200e11ba1fdc` |
| `polkachu/wasm-access-params.http.b64` | 774 | `9a44b1199695ef63aca044c2d91b30df0e78d0a08d9413190704d34d179bf938` | `ea483af6fc50cbb29a36ef194bb172a9a4d6793862c72a6e64f8200e11ba1fdc` |
