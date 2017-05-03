#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

"""
Product ID lookup table
"""

products = {"reynolds": {"daily":     "REY00001",
                         "monthly":   "REY00002",
                         "yearly":    "REY00003",
                         "3monthly":  "REY00004",
                         "6monthly":  "REY00005",
                         "12monthly": "REY00006",
                         "weekly":    "REY00007",
                         "yearlyAve": "REY00101",
                         "monthlyAve":"REY00102",
                         "weeklyDec":"REY00200",
                         "monthlyDec":"REY00201",
                         "3monthlyDec":"REY00202",
                         "6monthlyDec":"REY00203",
                         "12monthlyDec":"REY00204"
                        },
            "ersst": {"monthly":       "ERA00001",
                      "3monthly":      "ERA00002",
                      "6monthly":      "ERA00003",
                      "12monthly":     "ERA00004",
                      "monthlyAve":    "ERA00101",
                      "3monthlyAve":   "ERA00102",
                      "6monthlyAve":   "ERA00103",
                      "12monthlyAve":  "ERA00104",
                      "monthlyDec":    "ERA00201",# Decile ID
                      "3monthlyDec":   "ERA00202",
                      "6monthlyDec":   "ERA00203",
                      "12monthlyDec":  "ERA00204",
                      "monthlyTre":    "ERA00301",# Trend ID
                      "3monthlyTre":   "ERA00302",
                      "6monthlyTre":   "ERA00303",
                      "yearlyTre":     "ERA00304"
                     },
            "bran": {"monthly":       "BRN00001",
                     "3monthly":      "BRN00002",
                     "6monthly":      "BRN00003",
                     "12monthly":     "BRN00004",
                    },
            "ww3": {"point":  "WAV00001",
                    "rect": "WAV00002",
                    "hourly": "WAV00003",
                   },
            "sealevel": {"point": "SEA00001",
                         "monthly": "SEA00002",
                          "daily": "SEA00003"
                        },
            "ww3forecast": {"7d":  "WFC00001"
                           },
            "coral": {"daily": "CRW00001",
                      "4weeks": "CRW00002",
                      "8weeks": "CRW00003",
                      "12weeks": "CRW00004"
            },
            "chloro": {"daily": "CRL00001",
                       "monthly": "CRL00002"
            },
            "poama": {"sla": "POA00001",
                      "ssta": "POA00002",
                      "sst": "POA00003"
            },
            "currentfc": {"7d":  "CFC00001"
            },
            "mur": {"daily":  "MUR00001"
            }


}

