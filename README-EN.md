# Douyin / TikTok Video ID Decoder (Snowflake-style)

*English Documentation · 2025 Edition · Validated with 73 Real Data Samples*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-Evil0ctal-red.svg)](https://github.com/evil0ctal)

> Decode `aweme_id` (64-bit unsigned integer) to extract **publish timestamp (second-precision)** and analyze the **low 32 bits** for time-series research, sharding/QPS inference, and risk control analysis. This tool has been validated with **73 real data samples** (53 from Douyin / 20 from TikTok).

---

## 1) TL;DR Summary

* **Bit Structure**

  * High 32 bits = **Unix Timestamp (seconds)**
  * Low 32 bits = **Uniqueness bits** (suspected "shard/machine + sequence", exact bit-width not publicly disclosed)
* **Accuracy (≤5 seconds as "close match")**

  * Validation samples: 73 total (53 Douyin / 20 TikTok)
  * Exact match: **0%**
  * ≤5 seconds error: **26.0%**
  * **Average absolute error**: **14.3 seconds** (max 49s, min 2s)
  * Error direction: **Negative bias** (decoded time is earlier than actual):

    * Douyin average error: **-12.98 seconds** (range -49 ~ -2)
    * TikTok average error: **-17.80 seconds** (range -31 ~ -7)
* **Interpretation**

  * High 32 bits **do carry second-level time information**, but with **consistent small deviation** from platform-returned `create_time` (typically -7 ~ -30 seconds), likely due to **reporting/storage timing, server aggregation delay, rounding/sampling, or different field semantics**.
  * Engineering recommendation: **Apply platform-specific second-level calibration** (see §5) to significantly improve alignment with your data source's `create_time`.

---

## 2) Core Features

### 🔍 Basic Decoding
- Extract Unix timestamp (second-precision)
- Output UTC and local timezone datetime
- Display low 32 bits in multiple formats (decimal/hexadecimal/binary)

### 🧬 Low 32-bit Multi-dimensional Analysis
| Scheme | Bit Division | Description |
|--------|-------------|-------------|
| Scheme 1 | `10+10+12` | Standard Snowflake division (datacenter+worker+sequence) |
| Scheme 2 | `8+8+16` | Modified version (larger sequence space) |
| Scheme 3 | `16+16` | **Recommended** (convenient for shard/sequence clustering) |
| Scheme 4 | `8+8+8+8` | Byte-level analysis |

### 📊 Statistical Analysis Features
- ✅ Sequence number duplication detection (identify batch uploads)
- ✅ Shard ID distribution statistics
- ✅ Time distribution analysis (time span, earliest/latest)
- ✅ Low byte pattern recognition
- ✅ Platform comparison (Douyin vs TikTok)

### ✨ Advanced Features
- **🎯 Algorithm Accuracy Validation**: Automatically validate decoding algorithm with real data
- **📈 Visualization**: ASCII graphical display of 64-bit structure
- **🔧 Reverse Construction**: Generate Snowflake-like IDs for testing

---

## 3) Key Findings from Validation

* **Systematic Negative Bias**:

  * Douyin: average **-12.98s**
  * TikTok: average **-17.80s**
  * Both platforms show **consistent negative bias**, indicating "ID timestamp" is typically **earlier** than your sample's `create_time` field.
* **Error Distribution**: Most errors fall in **-7 ~ -30s** range, with extremes up to **-49s**.
* **Low-bit Patterns & Duplicates**:

  * Example: sequence `0x0d23` (3363) appears in two Douyin samples; `0x4d1e` (19742) in TikTok samples.
  * Byte0 shows high frequency of `0x1e` in TikTok; `0x23` in Douyin (small sample size, indicative only).
  * These signals **support the "low bits contain sequence/shard"** engineering hypothesis, but exact bit-widths require larger sample validation.

---

## 4) Understanding the "Error"

> Why isn't it 100% accurate to the second?

* **Field Semantic Difference**: Platform-returned `create_time` might be **"content visible/online"** time or **"aggregation/storage completion"** time, while ID timestamp is closer to **"generation/allocation"** moment.
* **Pipeline & Caching**: Asynchronous operations and retries exist across multi-tier services (upload, review, transcoding, risk control, distribution, indexing).
* **Rounding/Sampling**: Internal second-level alignment/rounding can cause +/− several seconds.
* **Timezone Independent**: UTC/LA time displayed are calculated from the timestamp; not a timezone display issue.

> Conclusion: **ID's high 32 bits are sufficient for "time sorting, range filtering, approximate positioning"**.
> For **strict alignment** with platform `create_time` for "precise alerting/tracing", apply **platform-level calibration** (next section).

---

## 5) Practical Recommendation: Second-level Calibration

To better align with `create_time`, apply **platform-specific** fixed calibration values (configurable):

* Recommended initial values:

  * `offset_seconds_douyin = +13`
  * `offset_seconds_tiktok = +18`
* Usage: After decoding, `timestamp_sec += offset_seconds_*` before comparison/display.
* Expected effect:

  * Pull "negative bias" **back to 0 ~ +5 second** range
  * In practice, significantly improves "≤5 seconds error" match rate (actual effect depends on your sample source)
* Operationalization:

  * Make calibration values **configurable** (ENV or CLI parameters), support A/B adjustment
  * Periodically re-evaluate with recent samples, auto-tune (e.g., use **offset mean** of recent 10k samples as calibration)

> Note: Keep both "raw decoded timestamp" and "calibrated timestamp" fields for audit and tracing.

---

## 6) Research Roadmap for Low 32 Bits (For Engineers)

* **Same-second Sampling**: Collect as many `aweme_id`s from the same second, observe low-bit **increment and wrap-around** under different schemes
* **Fit Sequence Bit-width**: Estimate "sequence number bits" from wrap-around points (e.g., 0→N→0 pattern)
* **Shard Clustering**: Remaining high bits can be treated as "shard/machine", cluster and analyze QPS, geographic/IDC distribution per shard
* **Cross-platform Comparison**: Compare Douyin vs TikTok low-bit distributions to see if they're isomorphic, reducing false positives

> Current sample size is limited; `16+16` scheme is more convenient for quick clustering and visualization, but doesn't claim to be the true bit-width.

---

## 7) Quick Start

### 📦 Requirements
```bash
Python 3.9+
Dependencies: None (standard library only)
```

### 🚀 Basic Usage

#### Method 1: Run Full Demo
```bash
python decode_aweme_id.py
```
Automatically executes:
1. ✅ **Algorithm Validation** (using aweme_ids_output.json)
2. 📋 Basic decoding demo
3. 🔬 Low 32-bit deep analysis
4. 📊 Statistical analysis and pattern recognition
5. 🎨 Bit structure visualization
6. 🔧 Reverse construction example

#### Method 2: Validation Only
```bash
python test_validation.py
```

#### Method 3: Use in Code
```python
from decode_aweme_id import decode_aweme_id, validate_decode_algorithm

# Decode single ID
result = decode_aweme_id("7350810998023949599")
print(result['datetime_utc'])  # Output UTC time

# Run full validation
validate_decode_algorithm()
```

### 📄 Data Format

**Input file**: `aweme_ids_output.json`

```json
{
  "total_count": 73,
  "douyin_count": 53,
  "tiktok_count": 20,
  "videos": [
    {
      "aweme_id": "7350810998023949599",
      "create_time": 1711494099,
      "create_datetime": "2024-03-26 19:34:59",
      "source": "Douyin"
    }
  ]
}
```

### 📤 Output Contents

After running the script, you'll get:

| Module | Description |
|--------|-------------|
| **Algorithm Validation** | Accuracy stats, error analysis, platform comparison |
| **Basic Decoding** | Timestamp, UTC/local time, low 32-bit representations |
| **Low-bit Analysis** | Detailed breakdown using 4 schemes |
| **Statistical Analysis** | Sequence duplicates, shard distribution, time span |
| **Visualization** | 64-bit binary structure ASCII diagram |
| **Construction Test** | Reverse generate ID and verify |

> Partial output:

```bash
[Douyin] 7153549929326120227
  实际时间 / Actual time: 2022-10-12 02:07:20 (ts: 1665565640)
  解码时间 / Decoded time: 2022-10-12T09:07:14+00:00 (ts: 1665565634)
  ✗ 误差 / Error (-6秒 / seconds)

[Douyin] 7266740902494833931
  实际时间 / Actual time: 2023-08-13 02:46:09 (ts: 1691919969)
  解码时间 / Decoded time: 2023-08-13T09:46:01+00:00 (ts: 1691919961)
  ✗ 误差 / Error (-8秒 / seconds)

[Douyin] 7553588363032005946
  实际时间 / Actual time: 2025-09-24 02:40:46 (ts: 1758706846)
  解码时间 / Decoded time: 2025-09-24T09:40:40+00:00 (ts: 1758706840)
  ✗ 误差 / Error (-6秒 / seconds)

[Douyin] 7542102211314076986
  实际时间 / Actual time: 2025-08-24 03:48:38 (ts: 1756032518)
  解码时间 / Decoded time: 2025-08-24T10:48:32+00:00 (ts: 1756032512)
  ✗ 误差 / Error (-6秒 / seconds)

[Douyin] 7506081353857207609
  实际时间 / Actual time: 2025-05-19 02:09:18 (ts: 1747645758)
  解码时间 / Decoded time: 2025-05-19T09:09:12+00:00 (ts: 1747645752)
  ✗ 误差 / Error (-6秒 / seconds)

[Douyin] 7502379797902216484
  实际时间 / Actual time: 2025-05-09 02:45:28 (ts: 1746783928)
  解码时间 / Decoded time: 2025-05-09T09:45:17+00:00 (ts: 1746783917)
  ✗ 误差 / Error (-11秒 / seconds)

[Douyin] 7502000723766430988
  实际时间 / Actual time: 2025-05-08 02:14:29 (ts: 1746695669)
  解码时间 / Decoded time: 2025-05-08T09:14:17+00:00 (ts: 1746695657)
  ✗ 误差 / Error (-12秒 / seconds)

[Douyin] 7490506246395563300
  实际时间 / Actual time: 2025-04-07 02:50:12 (ts: 1744019412)
  解码时间 / Decoded time: 2025-04-07T09:49:50+00:00 (ts: 1744019390)
  ✗ 误差 / Error (-22秒 / seconds)

[Douyin] 7488278337312263460
  实际时间 / Actual time: 2025-04-01 02:44:35 (ts: 1743500675)
  解码时间 / Decoded time: 2025-04-01T09:44:25+00:00 (ts: 1743500665)
  ✗ 误差 / Error (-10秒 / seconds)

[Douyin] 7484211357902966079
  实际时间 / Actual time: 2025-03-21 03:42:43 (ts: 1742553763)
  解码时间 / Decoded time: 2025-03-21T10:42:27+00:00 (ts: 1742553747)
  ✗ 误差 / Error (-16秒 / seconds)

[Douyin] 7477512161175080255
  实际时间 / Actual time: 2025-03-03 01:26:23 (ts: 1740993983)
  解码时间 / Decoded time: 2025-03-03T09:26:09+00:00 (ts: 1740993969)
  ✗ 误差 / Error (-14秒 / seconds)

[Douyin] 7476417322140437796
  实际时间 / Actual time: 2025-02-28 02:37:56 (ts: 1740739076)
  解码时间 / Decoded time: 2025-02-28T10:37:37+00:00 (ts: 1740739057)
  ✗ 误差 / Error (-19秒 / seconds)

[Douyin] 7475679294484729124
  实际时间 / Actual time: 2025-02-26 02:54:05 (ts: 1740567245)
  解码时间 / Decoded time: 2025-02-26T10:53:41+00:00 (ts: 1740567221)
  ✗ 误差 / Error (-24秒 / seconds)

[Douyin] 7473824079032749323
  实际时间 / Actual time: 2025-02-21 02:54:41 (ts: 1740135281)
  解码时间 / Decoded time: 2025-02-21T10:54:30+00:00 (ts: 1740135270)
  ✗ 误差 / Error (-11秒 / seconds)

[Douyin] 7473079802631589177
  实际时间 / Actual time: 2025-02-19 02:46:29 (ts: 1739961989)
  解码时间 / Decoded time: 2025-02-19T10:46:20+00:00 (ts: 1739961980)
  ✗ 误差 / Error (-9秒 / seconds)

[Douyin] 7471222653760654611
  实际时间 / Actual time: 2025-02-14 02:39:59 (ts: 1739529599)
  解码时间 / Decoded time: 2025-02-14T10:39:39+00:00 (ts: 1739529579)
  ✗ 误差 / Error (-20秒 / seconds)

[Douyin] 7468236778898459943
  实际时间 / Actual time: 2025-02-06 01:33:20 (ts: 1738834400)
  解码时间 / Decoded time: 2025-02-06T09:32:56+00:00 (ts: 1738834376)
  ✗ 误差 / Error (-24秒 / seconds)

[Douyin] 7467859527912770870
  实际时间 / Actual time: 2025-02-05 01:09:35 (ts: 1738746575)
  解码时间 / Decoded time: 2025-02-05T09:09:00+00:00 (ts: 1738746540)
  ✗ 误差 / Error (-35秒 / seconds)

[Douyin] 7464176276731890983
  实际时间 / Actual time: 2025-01-26 02:56:29 (ts: 1737888989)
  解码时间 / Decoded time: 2025-01-26T10:56:06+00:00 (ts: 1737888966)
  ✗ 误差 / Error (-23秒 / seconds)

[Douyin] 7461944739479194899
  实际时间 / Actual time: 2025-01-20 02:37:09 (ts: 1737369429)
  解码时间 / Decoded time: 2025-01-20T10:36:36+00:00 (ts: 1737369396)
  ✗ 误差 / Error (-33秒 / seconds)

[Douyin] 7455641451033005324
  实际时间 / Actual time: 2025-01-03 02:57:08 (ts: 1735901828)
  解码时间 / Decoded time: 2025-01-03T10:56:37+00:00 (ts: 1735901797)
  ✗ 误差 / Error (-31秒 / seconds)

[Douyin] 7454518969194630412
  实际时间 / Actual time: 2024-12-31 02:21:20 (ts: 1735640480)
  解码时间 / Decoded time: 2024-12-31T10:20:49+00:00 (ts: 1735640449)
  ✗ 误差 / Error (-31秒 / seconds)

[Douyin] 7454129794217790774
  实际时间 / Actual time: 2024-12-30 01:11:25 (ts: 1735549885)
  解码时间 / Decoded time: 2024-12-30T09:10:37+00:00 (ts: 1735549837)
  ✗ 误差 / Error (-48秒 / seconds)

[Douyin] 7453025153564298559
  实际时间 / Actual time: 2024-12-27 01:44:16 (ts: 1735292656)
  解码时间 / Decoded time: 2024-12-27T09:44:03+00:00 (ts: 1735292643)
  ✗ 误差 / Error (-13秒 / seconds)

[Douyin] 7451536968590150923
  实际时间 / Actual time: 2024-12-23 01:29:57 (ts: 1734946197)
  解码时间 / Decoded time: 2024-12-23T09:29:08+00:00 (ts: 1734946148)
  ✗ 误差 / Error (-49秒 / seconds)

[Douyin] 7449329569653460282
  实际时间 / Actual time: 2024-12-17 02:43:28 (ts: 1734432208)
  解码时间 / Decoded time: 2024-12-17T10:43:18+00:00 (ts: 1734432198)
  ✗ 误差 / Error (-10秒 / seconds)

[Douyin] 7444133391118683442
  实际时间 / Actual time: 2024-12-03 02:39:50 (ts: 1733222390)
  解码时间 / Decoded time: 2024-12-03T10:39:28+00:00 (ts: 1733222368)
  ✗ 误差 / Error (-22秒 / seconds)

[Douyin] 7443366116870720777
  实际时间 / Actual time: 2024-12-01 01:02:24 (ts: 1733043744)
  解码时间 / Decoded time: 2024-12-01T09:02:03+00:00 (ts: 1733043723)
  ✗ 误差 / Error (-21秒 / seconds)

[Douyin] 7441195561165851914
  实际时间 / Actual time: 2024-11-25 04:39:22 (ts: 1732538362)
  解码时间 / Decoded time: 2024-11-25T12:39:12+00:00 (ts: 1732538352)
  ✗ 误差 / Error (-10秒 / seconds)

[Douyin] 7432607934867180809
  实际时间 / Actual time: 2024-11-02 02:15:06 (ts: 1730538906)
  解码时间 / Decoded time: 2024-11-02T09:14:49+00:00 (ts: 1730538889)
  ✗ 误差 / Error (-17秒 / seconds)

[Douyin] 7426764196366339354
  实际时间 / Actual time: 2024-10-17 08:18:21 (ts: 1729178301)
  解码时间 / Decoded time: 2024-10-17T15:18:08+00:00 (ts: 1729178288)
  ✗ 误差 / Error (-13秒 / seconds)

[Douyin] 7424444791112338697
  实际时间 / Actual time: 2024-10-11 02:17:53 (ts: 1728638273)
  解码时间 / Decoded time: 2024-10-11T09:17:39+00:00 (ts: 1728638259)
  ✗ 误差 / Error (-14秒 / seconds)

[Douyin] 7395877358483328307
  实际时间 / Actual time: 2024-07-26 02:41:34 (ts: 1721986894)
  解码时间 / Decoded time: 2024-07-26T09:41:25+00:00 (ts: 1721986885)
  ✗ 误差 / Error (-9秒 / seconds)

[Douyin] 7391056989352168714
  实际时间 / Actual time: 2024-07-13 02:56:12 (ts: 1720864572)
  解码时间 / Decoded time: 2024-07-13T09:55:56+00:00 (ts: 1720864556)
  ✗ 误差 / Error (-16秒 / seconds)

[TikTok] 7559684939684400414
  实际时间 / Actual time: 2025-10-10 12:58:53 (ts: 1760126333)
  解码时间 / Decoded time: 2025-10-10T19:58:30+00:00 (ts: 1760126310)
  ✗ 误差 / Error (-23秒 / seconds)

[TikTok] 7559661864628538654
  实际时间 / Actual time: 2025-10-10 11:29:21 (ts: 1760120961)
  解码时间 / Decoded time: 2025-10-10T18:28:57+00:00 (ts: 1760120937)
  ✗ 误差 / Error (-24秒 / seconds)

[TikTok] 7559607368695188766
  实际时间 / Actual time: 2025-10-10 07:57:50 (ts: 1760108270)
  解码时间 / Decoded time: 2025-10-10T14:57:29+00:00 (ts: 1760108249)
  ✗ 误差 / Error (-21秒 / seconds)

[TikTok] 7559309513321352478
  实际时间 / Actual time: 2025-10-09 12:41:46 (ts: 1760038906)
  解码时间 / Decoded time: 2025-10-09T19:41:39+00:00 (ts: 1760038899)
  ✗ 误差 / Error (-7秒 / seconds)

[TikTok] 7558891371189325087
  实际时间 / Actual time: 2025-10-08 09:39:16 (ts: 1759941556)
  解码时间 / Decoded time: 2025-10-08T16:39:03+00:00 (ts: 1759941543)
  ✗ 误差 / Error (-13秒 / seconds)

[TikTok] 7558545854957751582
  实际时间 / Actual time: 2025-10-07 11:18:30 (ts: 1759861110)
  解码时间 / Decoded time: 2025-10-07T18:18:16+00:00 (ts: 1759861096)
  ✗ 误差 / Error (-14秒 / seconds)

[TikTok] 7558516087483010334
  实际时间 / Actual time: 2025-10-07 09:22:54 (ts: 1759854174)
  解码时间 / Decoded time: 2025-10-07T16:22:45+00:00 (ts: 1759854165)
  ✗ 误差 / Error (-9秒 / seconds)

[TikTok] 7558500140869225758
  实际时间 / Actual time: 2025-10-07 08:21:08 (ts: 1759850468)
  解码时间 / Decoded time: 2025-10-07T15:20:52+00:00 (ts: 1759850452)
  ✗ 误差 / Error (-16秒 / seconds)

[TikTok] 7558142881173671199
  实际时间 / Actual time: 2025-10-06 09:15:02 (ts: 1759767302)
  解码时间 / Decoded time: 2025-10-06T16:14:31+00:00 (ts: 1759767271)
  ✗ 误差 / Error (-31秒 / seconds)

[TikTok] 7557835825778560287
  实际时间 / Actual time: 2025-10-05 13:23:19 (ts: 1759695799)
  解码时间 / Decoded time: 2025-10-05T20:22:59+00:00 (ts: 1759695779)
  ✗ 误差 / Error (-20秒 / seconds)

[TikTok] 7556652844523310367
  实际时间 / Actual time: 2025-10-02 08:52:53 (ts: 1759420373)
  解码时间 / Decoded time: 2025-10-02T15:52:25+00:00 (ts: 1759420345)
  ✗ 误差 / Error (-28秒 / seconds)

[TikTok] 7556308975713537311
  实际时间 / Actual time: 2025-10-01 10:38:28 (ts: 1759340308)
  解码时间 / Decoded time: 2025-10-01T17:38:02+00:00 (ts: 1759340282)
  ✗ 误差 / Error (-26秒 / seconds)

[TikTok] 7556036906631318815
  实际时间 / Actual time: 2025-09-30 17:02:28 (ts: 1759276948)
  解码时间 / Decoded time: 2025-10-01T00:02:16+00:00 (ts: 1759276936)
  ✗ 误差 / Error (-12秒 / seconds)

[TikTok] 7556029213594144031
  实际时间 / Actual time: 2025-09-30 16:32:40 (ts: 1759275160)
  解码时间 / Decoded time: 2025-09-30T23:32:25+00:00 (ts: 1759275145)
  ✗ 误差 / Error (-15秒 / seconds)

[TikTok] 7556009541616389407
  实际时间 / Actual time: 2025-09-30 15:16:29 (ts: 1759270589)
  解码时间 / Decoded time: 2025-09-30T22:16:05+00:00 (ts: 1759270565)
  ✗ 误差 / Error (-24秒 / seconds)

[TikTok] 7555940417905134878
  实际时间 / Actual time: 2025-09-30 10:48:20 (ts: 1759254500)
  解码时间 / Decoded time: 2025-09-30T17:47:50+00:00 (ts: 1759254470)
  ✗ 误差 / Error (-30秒 / seconds)

[TikTok] 7555600450024721694
  实际时间 / Actual time: 2025-09-29 12:48:47 (ts: 1759175327)
  解码时间 / Decoded time: 2025-09-29T19:48:35+00:00 (ts: 1759175315)
  ✗ 误差 / Error (-12秒 / seconds)

[TikTok] 7555526907157040414
  实际时间 / Actual time: 2025-09-29 08:03:22 (ts: 1759158202)
  解码时间 / Decoded time: 2025-09-29T15:03:12+00:00 (ts: 1759158192)
  ✗ 误差 / Error (-10秒 / seconds)

[TikTok] 7554123030205713694
  实际时间 / Actual time: 2025-09-25 13:15:39 (ts: 1758831339)
  解码时间 / Decoded time: 2025-09-25T20:15:27+00:00 (ts: 1758831327)
  ✗ 误差 / Error (-12秒 / seconds)

[TikTok] 7554044414469917982
  实际时间 / Actual time: 2025-09-25 08:10:32 (ts: 1758813032)
  解码时间 / Decoded time: 2025-09-25T15:10:23+00:00 (ts: 1758813023)
  ✗ 误差 / Error (-9秒 / seconds)

================================================================================
=== 验证结果统计 / Validation Results Statistics ===
================================================================================

📊 总体准确性 / Overall Accuracy:
  验证总数 / Total validated:     73
  完全匹配 / Exact match:     0 (0.0%)
  接近匹配 / Close match:     19 (26.0%)
  较大误差 / Large error:     54

📈 误差分析 (绝对值) / Error Analysis (Absolute Value):
  平均误差 / Average error:     14.30 秒 / seconds
  最大误差 / Maximum error:     49 秒 / seconds
  最小误差 / Minimum error:     2 秒 / seconds

🇨🇳 抖音平台 / Douyin Platform:
  数量 / Count:         53
  平均误差 / Average error:     -12.98 秒 / seconds
  误差范围 / Error range:     -49 ~ -2 秒 / seconds

🌐 TikTok平台 / TikTok Platform:
  数量 / Count:         20
  平均误差 / Average error:     -17.80 秒 / seconds
  误差范围 / Error range:     -31 ~ -7 秒 / seconds

```

---

## 8) Project Structure

```
./
├── decode_aweme_id.py          # 🔧 Core script (decode/analyze/validate)
├── test_validation.py          # ✅ Quick validation script
├── aweme_ids_output.json       # 📊 Real sample data (73 entries)
├── README.md                   # 📖 Chinese Documentation
├── README-EN.md                # 📖 English Documentation
└── config.example.toml         # ⚙️  Optional config (calibration params)
```

### Optional Configuration File

`config.example.toml`:

```toml
[calibration]
# Second-level calibration parameters (based on error analysis)
douyin_offset_seconds = 13
tiktok_offset_seconds = 18

[analysis]
# Analysis parameters
close_match_threshold = 5  # Close match threshold (seconds)
```

---

## 9) Real-world Applications

### 🎯 Data Analysis
- **Time-series Research**: Filter videos by time range without database queries
- **Publishing Pattern Analysis**: Identify peak hours, publishing frequency
- **Content Freshness**: Quickly determine content age

### 🔍 System Monitoring
- **Distributed Tracing**: Locate server/IDC via shard ID
- **Performance Analysis**: Estimate QPS, load balancing effectiveness via sequence numbers
- **Anomaly Detection**: Identify batch uploads, crawler behavior

### 🛡️ Risk Control & Security
- **Batch Identification**: Same sequence numbers may indicate batch operations
- **Time Verification**: Validate ID-business time reasonableness
- **Deduplication Optimization**: Efficient deduplication strategies based on ID structure

### 📊 Data Collection
- **Incremental Collection**: Precisely control collection window by timestamp range
- **Data Backtracking**: Quickly locate content from specific time periods
- **Collection Quality**: Verify time-series completeness of collected data

---

## 10) FAQ

### Q1: Why isn't exact match rate 100%?
**A**: This is normal. ID timestamp is the generation moment, while API-returned `create_time` might be review approval, content online, or other moments. Errors are typically within ±20 seconds.

### Q2: How to improve match with create_time?
**A**: Use calibration scheme in §5, add platform-specific offsets:
- Douyin: +13 seconds
- TikTok: +18 seconds

### Q3: Can low 32 bits be fully recovered?
**A**: Cannot be directly recovered from public information. Recommend using §6 methods, through same-second sampling and statistical analysis to find the most suitable division scheme for your data.

### Q4: Which timezones are supported?
**A**: Defaults to UTC and Los Angeles timezone. You can modify the `LA_TZ` variable in the script to any timezone (e.g., `Asia/Shanghai`).

### Q5: Can reverse-constructed IDs be used in production?
**A**: No. `forge_aweme_like_id()` is only for testing, sorting, integration testing, and other local scenarios; doesn't correspond to real platform content.

### Q6: What data does validation require?
**A**: Requires JSON file containing `aweme_id`, `create_time`, `source` fields. Format reference: `aweme_ids_output.json`.

### Q7: How to add my own test data?
**A**: Organize your data according to §7 JSON format, save as `aweme_ids_output.json`, then run `validate_decode_algorithm()`.

---

## 11) Version Information

| Info | Content |
|------|---------|
| **Version** | v2.0 (2025) |
| **Author** | Evil0ctal (Adam) |
| **License** | MIT License |
| **Python** | 3.9+ |
| **Dependencies** | No external dependencies |

## 12) Changelog

### v2.0 (2025-01)
- ✨ Added `validate_decode_algorithm()` auto-validation feature
- ✨ Added `test_validation.py` quick test script
- 📊 Complete validation report based on 73 real data samples
- 📖 Restructured documentation, improved structure and readability
- 🌐 Added English documentation README-EN.md

### v1.0 (2024)
- 🎉 Initial release
- 🔧 Basic decoding functionality
- 📊 Low 32-bit multi-scheme analysis
- 📈 Statistical analysis and visualization

## 13) Acknowledgments

- 💙 Thanks to [TikHub.io](https://tikhub.io/) for providing real sample data
- 🙏 Thanks to the open-source community for Snowflake ID algorithm research
- 🌟 Thanks to all contributors and users for feedback

## 14) Contact

- **GitHub**: [@evil0ctal](https://github.com/evil0ctal)
- **Project**: [Douyin-TikTok-Video-ID-Decoder](https://github.com/Evil0ctal/Douyin-TikTok-Video-ID-Decoder)
- **Issue Tracker**: [GitHub Issues](https://github.com/Evil0ctal/Douyin-TikTok-Video-ID-Decoder/issues)

---

<div align="center">

**⭐ If this project helps you, please give it a Star!**

Made with ❤️ by Evil0ctal

</div>
