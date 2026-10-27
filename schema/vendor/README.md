# Pinned standards

Local copies of the standards the AI Factory Ontology extends or uses. Validation reads these files, never the network.

| File | Standard | Version | Source or version IRI | License | sha256 |
|---|---|---|---|---|---|
| `brick.ttl` | Brick | 1.4.4 | https://github.com/BrickSchema/Brick/releases/download/v1.4.4/Brick.ttl (retrieved 2026-10-25) | BSD-3-Clause, Copyright 2016-2023 Brick Consortium (`brick-LICENSE.txt`); a few definitions quote the ASHRAE Dictionary and are outside that license | `b65720b7b9b64c646745c689777e6138c0d59ce0088df0aeb78fbd444d04d8e7` |
| `ashrae-223.ttl` | ASHRAE Standard 223 | open223 master `6fdc11c60b930ccb042d775b66a9115547fd22a7` (2026-10-06) | https://data.ashrae.org/standard223/223p.ttl (retrieved 2026-10-25) | Apache-2.0 as declared in the model file (`ashrae-223-LICENSE-2.0.txt`); the ASHRAE website states no license. To confirm before release. | `9a4d5f0dfc88ab029d816c376ed804da388295395db4448d5706525a82795749` |
| `qudt-schema.ttl` | QUDT schema | 3.5.3 | version IRI http://qudt.org/3.5.3/schema/qudt (download URL not recorded) | CC BY 4.0 | `807b5b03a8759670a6412822c7624cc6180c5e80ff7b9b3b8e4bee98e1c1c882` |
| `qudt-unit.ttl` | QUDT units | 3.5.3 | version IRI http://qudt.org/3.5.3/vocab/unit (download URL not recorded) | CC BY 4.0 | `89df26d7f8ebb54a80d6bd4e03f3268b16a7acdc7b90490346273c03817971d4` |
| `qudt-quantitykind.ttl` | QUDT quantity kinds | 3.5.3 | https://qudt.org/3.5.3/vocab/quantitykind (retrieved 2026-10-26) | CC BY 4.0 | `730052a9a760f0f70ac389e8d7e493a729bc8ea2e5f226af68a4b279e7232d81` |
| `oa.ttl` | W3C Web Annotation Vocabulary | 2016-11-12 | https://www.w3.org/ns/oa.ttl (retrieved 2026-10-27) | W3C Software and Document License | `f661e37d33bf29176390101687711734a7e33a716bdecfb66b90c732373d7af5` |
| `prov-o.ttl` | W3C PROV-O | 2013 Recommendation | http://www.w3.org/ns/prov-o | W3C Software and Document License | `7d203989f67b38bca572253942acc5a1bf24ce3ccfece16f072dcb4be2b79a96` |
| `skos.rdf` | W3C SKOS | 2009 Recommendation | http://www.w3.org/2004/02/skos/core | W3C Software and Document License | `e79633b8d0564816cee8a99f5c9acf9a0e6fc7257c7209acd684ecad53a89dd6` |
| `dcterms.ttl` | DCMI Metadata Terms | 2020-01-20 | http://purl.org/dc/terms/ | CC BY 4.0 | `13df401072dd7015bf9d75162f3e41c8138075304b7b9cc1aa1e9c16db976797` |

QUDT is licensed under Creative Commons Attribution 4.0 (https://creativecommons.org/licenses/by/4.0/). Its `dcterms:rights` statement also notes content derived from UCUM under a license from Regenstrief Institute and The UCUM Organization; both notices travel with any release.

Brick 1.4.4 imports QUDT 3.1.0 and ASHRAE 223 imports QUDT 3.4.0. Our files reference units and quantity kinds by IRI, and a test checks that every IRI we use exists in the 3.5.3 copies above.

Replacing a file means updating its row, its checksum and `docs/CHANGELOG.md` in the same commit.
