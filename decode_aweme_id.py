#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音 / TikTok 视频 ID 解密算法 (Snowflake 风格)
Douyin / TikTok Video ID Decoder (Snowflake Style)

作者 / Author: Evil0ctal

说明 / Description:
  - 抖音与 TikTok 的视频 ID（aweme_id）是 64 位无符号整数。
    Douyin and TikTok video IDs (aweme_id) are 64-bit unsigned integers.
  - 高 32 位 = Unix 时间戳（秒级，单位：s）
    High 32 bits = Unix timestamp (second-level, unit: s)
  - 低 32 位 = 唯一性位（分片ID + 序列号）
    Low 32 bits = Uniqueness bits (shard ID + sequence number)
  - 结构与 Twitter 的 Snowflake 类似，只是时间精度不同（Snowflake 是毫秒级）
    Similar to Twitter's Snowflake structure, but with different time precision (Snowflake uses milliseconds)
"""

import json
import secrets
import zoneinfo
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# 设置时区（可自行更改）
# Set timezone (can be customized)
LA_TZ = zoneinfo.ZoneInfo("America/Los_Angeles")


def decode_aweme_id(id_str: str, analyze_low32: bool = False) -> Dict[str, Any]:
    """
    解码抖音 / TikTok 视频 ID（十进制字符串）
    Decode Douyin / TikTok video ID (decimal string)

    :param id_str: 视频 ID（十进制字符串）/ Video ID (decimal string)
    :param analyze_low32: 是否深度分析低32位结构 / Whether to analyze low 32-bit structure in depth
    :return: 包含时间戳、日期、低位字段的详细字典 / Detailed dictionary containing timestamp, date, and low-bit fields
    """
    n = int(id_str)
    ts_sec = n >> 32  # 高 32 位：秒级时间戳 / High 32 bits: second-level timestamp
    low32 = n & 0xFFFFFFFF  # 低 32 位：唯一性位（机器 + 序列号）/ Low 32 bits: uniqueness bits (machine + sequence)

    dt_utc = datetime.fromtimestamp(ts_sec, tz=timezone.utc)
    dt_la = dt_utc.astimezone(LA_TZ)

    result = {
        "id": id_str,
        "timestamp_sec": str(ts_sec),
        "datetime_utc": dt_utc.isoformat(),
        "datetime_America/Los_Angeles": dt_la.isoformat(),
        "low32_dec": str(low32),
        "low32_hex": hex(low32),
        "low32_bin": bin(low32),
    }

    # 深度分析低32位的可能结构
    # Deep analysis of possible low 32-bit structures
    if analyze_low32:
        # 尝试不同的位划分方案
        # Try different bit division schemes

        # 方案1: 标准 Snowflake (10+10+12)
        # Scheme 1: Standard Snowflake (10+10+12)
        scheme1 = {
            "datacenter_id": (low32 >> 22) & 0x3FF,  # 高10位 / High 10 bits
            "worker_id": (low32 >> 12) & 0x3FF,      # 中10位 / Middle 10 bits
            "sequence": low32 & 0xFFF,                # 低12位 / Low 12 bits
        }

        # 方案2: 修改版 (8+8+16)
        # Scheme 2: Modified version (8+8+16)
        scheme2 = {
            "datacenter_id": (low32 >> 24) & 0xFF,   # 高8位 / High 8 bits
            "worker_id": (low32 >> 16) & 0xFF,       # 中8位 / Middle 8 bits
            "sequence": low32 & 0xFFFF,               # 低16位 / Low 16 bits
        }

        # 方案3: 简化版 (16+16)
        # Scheme 3: Simplified version (16+16)
        scheme3 = {
            "shard_id": (low32 >> 16) & 0xFFFF,      # 高16位 / High 16 bits
            "sequence": low32 & 0xFFFF,               # 低16位 / Low 16 bits
        }

        # 方案4: 字节划分 (8+8+8+8)
        # Scheme 4: Byte division (8+8+8+8)
        scheme4 = {
            "byte3": (low32 >> 24) & 0xFF,
            "byte2": (low32 >> 16) & 0xFF,
            "byte1": (low32 >> 8) & 0xFF,
            "byte0": low32 & 0xFF,
        }

        result["low32_analysis"] = {
            "scheme1_10_10_12": scheme1,
            "scheme2_8_8_16": scheme2,
            "scheme3_16_16": scheme3,
            "scheme4_bytes": scheme4,
        }

    return result


def forge_aweme_like_id(ts_sec: int, low32: int | None = None) -> int:
    """
    构造一个"类抖音风格"的视频 ID（用于测试验证）
    Forge a "Douyin-style" video ID (for testing and verification)

    :param ts_sec: 秒级时间戳（int）/ Second-level timestamp (int)
    :param low32: 自定义低 32 位整数（可选）/ Custom low 32-bit integer (optional)
    :return: 构造出的 64 位整数 / Constructed 64-bit integer
    """
    if low32 is None:
        low32 = secrets.randbits(32)
    return (ts_sec << 32) | (low32 & 0xFFFFFFFF)


def batch_decode(ids: List[str]) -> None:
    """
    批量解码多个视频 ID
    Batch decode multiple video IDs
    """
    for i, aweme_id in enumerate(ids, start=1):
        result = decode_aweme_id(aweme_id)
        print(f"\n[{i}] ID: {aweme_id}")
        print(f"  发布时间(UTC): {result['datetime_utc']}")
        print(f"  发布时间(LA):  {result['datetime_America/Los_Angeles']}")
        print(f"  时间戳秒数:   {result['timestamp_sec']}")
        print(f"  低32位(十进制): {result['low32_dec']}")
        print(f"  低32位(十六进制): {result['low32_hex']}")
        print(f"  低32位(二进制): {result['low32_bin']}")


def deep_analyze_low32(ids: List[str]) -> None:
    """
    深度分析低32位的结构，寻找规律
    Deep analysis of low 32-bit structure to find patterns
    """
    print("\n" + "=" * 80)
    print("=== 低32位深度分析 / Low 32-bit Deep Analysis ===")
    print("=" * 80)

    for i, aweme_id in enumerate(ids, start=1):
        result = decode_aweme_id(aweme_id, analyze_low32=True)
        analysis = result["low32_analysis"]

        print(f"\n[{i}] ID: {aweme_id}")
        print(f"  低32位: {result['low32_bin']} ({result['low32_hex']})")
        print(f"\n  方案1 (标准 Snowflake: 10+10+12 位) / Scheme 1 (Standard Snowflake: 10+10+12 bits)")
        print(f"    数据中心ID / Datacenter ID: {analysis['scheme1_10_10_12']['datacenter_id']:4d} (0x{analysis['scheme1_10_10_12']['datacenter_id']:03x})")
        print(f"    机器ID / Worker ID:        {analysis['scheme1_10_10_12']['worker_id']:4d} (0x{analysis['scheme1_10_10_12']['worker_id']:03x})")
        print(f"    序列号 / Sequence:          {analysis['scheme1_10_10_12']['sequence']:4d} (0x{analysis['scheme1_10_10_12']['sequence']:03x})")

        print(f"\n  方案2 (修改版: 8+8+16 位) / Scheme 2 (Modified: 8+8+16 bits)")
        print(f"    数据中心ID / Datacenter ID: {analysis['scheme2_8_8_16']['datacenter_id']:4d} (0x{analysis['scheme2_8_8_16']['datacenter_id']:02x})")
        print(f"    机器ID / Worker ID:        {analysis['scheme2_8_8_16']['worker_id']:4d} (0x{analysis['scheme2_8_8_16']['worker_id']:02x})")
        print(f"    序列号 / Sequence:          {analysis['scheme2_8_8_16']['sequence']:6d} (0x{analysis['scheme2_8_8_16']['sequence']:04x})")

        print(f"\n  方案3 (简化版: 16+16 位) / Scheme 3 (Simplified: 16+16 bits)")
        print(f"    分片ID / Shard ID:          {analysis['scheme3_16_16']['shard_id']:6d} (0x{analysis['scheme3_16_16']['shard_id']:04x})")
        print(f"    序列号 / Sequence:          {analysis['scheme3_16_16']['sequence']:6d} (0x{analysis['scheme3_16_16']['sequence']:04x})")

        print(f"\n  方案4 (字节划分: 8+8+8+8 位) / Scheme 4 (Byte division: 8+8+8+8 bits)")
        print(f"    字节3 (高) / Byte3 (High):  {analysis['scheme4_bytes']['byte3']:3d} (0x{analysis['scheme4_bytes']['byte3']:02x})")
        print(f"    字节2 / Byte2:              {analysis['scheme4_bytes']['byte2']:3d} (0x{analysis['scheme4_bytes']['byte2']:02x})")
        print(f"    字节1 / Byte1:              {analysis['scheme4_bytes']['byte1']:3d} (0x{analysis['scheme4_bytes']['byte1']:02x})")
        print(f"    字节0 (低) / Byte0 (Low):   {analysis['scheme4_bytes']['byte0']:3d} (0x{analysis['scheme4_bytes']['byte0']:02x})")


def statistical_analysis(ids: List[str], platform_labels: List[str] = None) -> None:
    """
    统计分析：找出ID之间的相关性和模式
    Statistical analysis: Find correlations and patterns between IDs

    :param ids: 视频ID列表 / List of video IDs
    :param platform_labels: 平台标签列表（可选，如 ['Douyin', 'TikTok']）/ Platform label list (optional, e.g., ['Douyin', 'TikTok'])
    """
    print("\n" + "=" * 80)
    print("=== 统计分析与模式识别 / Statistical Analysis and Pattern Recognition ===")
    print("=" * 80)

    # 收集数据 / Collect data
    data = []
    for aweme_id in ids:
        result = decode_aweme_id(aweme_id, analyze_low32=True)
        data.append(result)

    # 分析方案3 (16+16位) - 最可能的方案
    # Analyze Scheme 3 (16+16 bits) - Most likely scheme
    print("\n【推荐方案 / Recommended Scheme】16+16位划分 (分片ID + 序列号) / 16+16 bit division (Shard ID + Sequence)")
    print("-" * 80)

    # 统计序列号分布 / Count sequence distribution
    sequence_counts = defaultdict(list)
    shard_counts = defaultdict(list)

    for i, d in enumerate(data):
        seq = d["low32_analysis"]["scheme3_16_16"]["sequence"]
        shard = d["low32_analysis"]["scheme3_16_16"]["shard_id"]
        label = platform_labels[i] if platform_labels else f"ID{i+1}"

        sequence_counts[seq].append((label, d["id"]))
        shard_counts[shard].append((label, d["id"]))

    # 找出重复的序列号 / Find duplicate sequences
    print("\n1️⃣  序列号重复检测 (可能来自同一批次/服务器) / Sequence Duplication Detection (may be from same batch/server):")
    duplicates = {k: v for k, v in sequence_counts.items() if len(v) > 1}
    if duplicates:
        for seq, ids_list in duplicates.items():
            print(f"\n   序列号 / Sequence {seq} (0x{seq:04x}) 出现 / Appears {len(ids_list)} 次 / times:")
            for label, vid in ids_list:
                print(f"     - [{label}] {vid}")
    else:
        print("   ✓ 所有序列号唯一 / All sequences are unique")

    # 分片ID统计 / Shard ID statistics
    print("\n2️⃣  分片ID分布 / Shard ID Distribution:")
    for shard, ids_list in sorted(shard_counts.items()):
        if len(ids_list) > 1:
            print(f"\n   分片 / Shard {shard:5d} (0x{shard:04x}): {len(ids_list)} 个视频 / videos")
            for label, vid in ids_list:
                print(f"     - [{label}] {vid}")
        else:
            label, vid = ids_list[0]
            print(f"   分片 / Shard {shard:5d} (0x{shard:04x}): [{label}] {vid}")

    # 时间分布 / Time distribution
    print("\n3️⃣  时间分布 / Time Distribution:")
    timestamps = [(d["timestamp_sec"], d["id"]) for d in data]
    timestamps.sort()

    print(f"   最早 / Earliest: {timestamps[0][0]} → {data[0]['datetime_utc']}")
    print(f"   最晚 / Latest: {timestamps[-1][0]} → {data[-1]['datetime_utc']}")

    time_diff = int(timestamps[-1][0]) - int(timestamps[0][0])
    print(f"   时间跨度 / Time span: {time_diff} 秒 / seconds ({time_diff/3600:.2f} 小时 / hours / {time_diff/86400:.2f} 天 / days)")

    # 低字节分析 / Low byte analysis
    print("\n4️⃣  低字节 (Byte0) 模式分析 / Low Byte (Byte0) Pattern Analysis:")
    byte0_counts = defaultdict(list)
    for i, d in enumerate(data):
        byte0 = d["low32_analysis"]["scheme4_bytes"]["byte0"]
        label = platform_labels[i] if platform_labels else f"ID{i+1}"
        byte0_counts[byte0].append(label)

    for byte0, labels in sorted(byte0_counts.items()):
        if len(labels) > 1:
            print(f"   0x{byte0:02x} ({byte0:3d}): {', '.join(labels)} ⭐ 重复 / Duplicate!")
        else:
            print(f"   0x{byte0:02x} ({byte0:3d}): {labels[0]}")

    # 平台对比（如果提供了标签）/ Platform comparison (if labels provided)
    if platform_labels:
        print("\n5️⃣  平台对比 / Platform Comparison:")
        platform_data = defaultdict(list)
        for i, d in enumerate(data):
            platform = platform_labels[i]
            platform_data[platform].append(d)

        for platform, pdata in platform_data.items():
            print(f"\n   【{platform}】 ({len(pdata)} 个视频 / videos)")
            seqs = [d["low32_analysis"]["scheme3_16_16"]["sequence"] for d in pdata]
            shards = [d["low32_analysis"]["scheme3_16_16"]["shard_id"] for d in pdata]

            print(f"     序列号范围 / Sequence range: {min(seqs)} - {max(seqs)}")
            print(f"     分片ID范围 / Shard ID range:  {min(shards)} - {max(shards)}")
            print(f"     唯一序列号 / Unique sequences:  {len(set(seqs))} / {len(seqs)}")
            print(f"     唯一分片ID / Unique shards:  {len(set(shards))} / {len(shards)}")


def load_test_data(json_path: str = "aweme_ids_output.json") -> Dict[str, Any]:
    """
    加载测试数据JSON文件
    Load test data JSON file

    :param json_path: JSON文件路径 / JSON file path
    :return: 解析后的JSON数据 / Parsed JSON data
    """
    file_path = Path(__file__).parent / json_path
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_decode_algorithm(json_path: str = "aweme_ids_output.json") -> None:
    """
    使用真实数据验证解码算法的准确性
    Validate decode algorithm accuracy using real data

    :param json_path: 测试数据JSON文件路径 / Test data JSON file path
    """
    print("\n" + "=" * 80)
    print("=== 解码算法准确性验证 / Decode Algorithm Accuracy Validation ===")
    print("=" * 80)

    # 加载测试数据 / Load test data
    test_data = load_test_data(json_path)
    videos = test_data["videos"]

    print(f"\n加载测试数据 / Loading test data:")
    print(f"  总数量 / Total count: {test_data['total_count']}")
    print(f"  抖音 / Douyin:   {test_data['douyin_count']}")
    print(f"  TikTok: {test_data['tiktok_count']}")

    # 统计数据 / Statistical data
    results = {
        "total": 0,
        "exact_match": 0,
        "close_match": 0,  # 误差在5秒内 / Error within 5 seconds
        "time_diffs": [],
        "douyin_diffs": [],
        "tiktok_diffs": [],
    }

    print("\n" + "-" * 80)
    print("开始验证 / Starting validation...")
    print("-" * 80)

    for video in videos:
        aweme_id = video["aweme_id"]
        actual_timestamp = video["create_time"]
        source = video["source"]
        create_datetime = video["create_datetime"]

        # 解码ID / Decode ID
        decoded = decode_aweme_id(aweme_id)
        decoded_timestamp = int(decoded["timestamp_sec"])

        # 计算时间差 / Calculate time difference
        time_diff = decoded_timestamp - actual_timestamp

        # 收集统计 / Collect statistics
        results["total"] += 1
        results["time_diffs"].append(abs(time_diff))

        if source == "Douyin":
            results["douyin_diffs"].append(time_diff)
        else:
            results["tiktok_diffs"].append(time_diff)

        # 分类 / Classify
        if time_diff == 0:
            results["exact_match"] += 1
            status = "✓ 完全匹配 / Exact match"
        elif abs(time_diff) <= 5:
            results["close_match"] += 1
            status = f"✓ 接近 / Close (误差 / error {time_diff:+d}秒 / seconds)"
        else:
            status = f"✗ 误差 / Error ({time_diff:+d}秒 / seconds)"

        # 仅打印误差较大的情况 / Only print cases with large errors
        if abs(time_diff) > 5:
            print(f"\n[{source}] {aweme_id}")
            print(f"  实际时间 / Actual time: {create_datetime} (ts: {actual_timestamp})")
            print(f"  解码时间 / Decoded time: {decoded['datetime_utc']} (ts: {decoded_timestamp})")
            print(f"  {status}")

    # 统计报告 / Statistics report
    print("\n" + "=" * 80)
    print("=== 验证结果统计 / Validation Results Statistics ===")
    print("=" * 80)

    print(f"\n📊 总体准确性 / Overall Accuracy:")
    print(f"  验证总数 / Total validated:     {results['total']}")
    print(f"  完全匹配 / Exact match:     {results['exact_match']} ({results['exact_match']/results['total']*100:.1f}%)")
    print(f"  接近匹配 / Close match:     {results['close_match']} ({results['close_match']/results['total']*100:.1f}%)")
    print(f"  较大误差 / Large error:     {results['total'] - results['exact_match'] - results['close_match']}")

    # 时间差分析 / Time difference analysis
    if results["time_diffs"]:
        avg_diff = sum(results["time_diffs"]) / len(results["time_diffs"])
        max_diff = max(results["time_diffs"])
        min_diff = min(results["time_diffs"])

        print(f"\n📈 误差分析 (绝对值) / Error Analysis (Absolute Value):")
        print(f"  平均误差 / Average error:     {avg_diff:.2f} 秒 / seconds")
        print(f"  最大误差 / Maximum error:     {max_diff} 秒 / seconds")
        print(f"  最小误差 / Minimum error:     {min_diff} 秒 / seconds")

    # 平台对比 / Platform comparison
    if results["douyin_diffs"]:
        douyin_avg = sum(results["douyin_diffs"]) / len(results["douyin_diffs"])
        print(f"\n🇨🇳 抖音平台 / Douyin Platform:")
        print(f"  数量 / Count:         {len(results['douyin_diffs'])}")
        print(f"  平均误差 / Average error:     {douyin_avg:+.2f} 秒 / seconds")
        print(f"  误差范围 / Error range:     {min(results['douyin_diffs']):+d} ~ {max(results['douyin_diffs']):+d} 秒 / seconds")

    if results["tiktok_diffs"]:
        tiktok_avg = sum(results["tiktok_diffs"]) / len(results["tiktok_diffs"])
        print(f"\n🌐 TikTok平台 / TikTok Platform:")
        print(f"  数量 / Count:         {len(results['tiktok_diffs'])}")
        print(f"  平均误差 / Average error:     {tiktok_avg:+.2f} 秒 / seconds")
        print(f"  误差范围 / Error range:     {min(results['tiktok_diffs']):+d} ~ {max(results['tiktok_diffs']):+d} 秒 / seconds")

    # 结论 / Conclusion
    print("\n" + "=" * 80)
    print("=== 结论 / Conclusion ===")
    print("=" * 80)

    accuracy_rate = (results["exact_match"] + results["close_match"]) / results["total"] * 100

    if accuracy_rate >= 95:
        conclusion = "✅ 算法准确性极高，高32位确实是Unix时间戳（秒级）/ Algorithm is highly accurate, high 32 bits are indeed Unix timestamp (second-level)"
    elif accuracy_rate >= 80:
        conclusion = "✅ 算法准确性较高，存在小幅时间偏移 / Algorithm accuracy is good, with minor time offset"
    else:
        conclusion = "⚠️  算法存在较大误差，需要进一步分析 / Algorithm has significant errors, needs further analysis"

    print(f"\n{conclusion}")
    print(f"准确率（≤5秒误差）/ Accuracy (≤5 sec error): {accuracy_rate:.1f}%")

    print("\n💡 解读 / Interpretation:")
    print("  • 高32位 / High 32 bits = Unix时间戳（秒级）/ Unix timestamp (second-level)")
    print("  • 低32位 / Low 32 bits = 分片ID + 序列号 / Shard ID + Sequence number")
    print("  • 误差可能来源 / Possible error sources：服务器时钟偏移、时区转换、视频上传延迟 / Server clock offset, timezone conversion, video upload delay")
    print("  • 算法可用于 / Algorithm can be used for：时间范围查询、时序分析、分布式追踪 / Time range query, time series analysis, distributed tracing")


def visualize_bit_structure(aweme_id: str) -> None:
    """
    可视化展示ID的位结构
    Visualize ID bit structure
    """
    print("\n" + "=" * 80)
    print("=== ID位结构可视化 / ID Bit Structure Visualization ===")
    print("=" * 80)

    result = decode_aweme_id(aweme_id, analyze_low32=True)
    n = int(aweme_id)

    # 64位二进制表示 / 64-bit binary representation
    bin_str = format(n, '064b')

    print(f"\nID: {aweme_id}")
    print(f"\n完整64位二进制 / Complete 64-bit Binary:")
    print("┌" + "─" * 32 + "┬" + "─" * 32 + "┐")
    print("│" + " " * 8 + "高32位 (时间戳)" + " " * 8 + "│" + " " * 8 + "低32位 (唯一性)" + " " * 8 + "│")
    print("│" + " " * 6 + "High 32 bits (Timestamp)" + " " * 6 + "│" + " " * 6 + "Low 32 bits (Uniqueness)" + " " * 6 + "│")
    print("├" + "─" * 32 + "┼" + "─" * 32 + "┤")

    # 分段显示 / Segmented display
    high32 = bin_str[:32]
    low32 = bin_str[32:]

    # 每8位一组显示 / Display in groups of 8 bits
    print("│ ", end="")
    for i in range(0, 32, 8):
        print(high32[i:i+8], end=" ")
    print("│ ", end="")
    for i in range(0, 32, 8):
        print(low32[i:i+8], end=" ")
    print("│")

    print("└" + "─" * 32 + "┴" + "─" * 32 + "┘")

    # 解析结果 / Parse result
    ts_sec = n >> 32
    low32_val = n & 0xFFFFFFFF

    print(f"\n高32位解析 / High 32-bit Parsing:")
    print(f"  二进制 / Binary: {high32}")
    print(f"  十进制 / Decimal: {ts_sec}")
    print(f"  时间 / Time:   {result['datetime_utc']}")

    print(f"\n低32位解析 (推荐方案: 16+16) / Low 32-bit Parsing (Recommended: 16+16):")
    analysis = result["low32_analysis"]["scheme3_16_16"]

    low32_bin = format(low32_val, '032b')
    shard_bin = low32_bin[:16]
    seq_bin = low32_bin[16:]

    print("┌" + "─" * 16 + "┬" + "─" * 16 + "┐")
    print("│  分片ID (16位) │  序列号 (16位) │")
    print("│  Shard ID (16) │ Sequence (16) │")
    print("├" + "─" * 16 + "┼" + "─" * 16 + "┤")
    print(f"│ {shard_bin[:8]} {shard_bin[8:]} │ {seq_bin[:8]} {seq_bin[8:]} │")
    print("└" + "─" * 16 + "┴" + "─" * 16 + "┘")

    print(f"  分片ID / Shard ID: {analysis['shard_id']:6d} (0x{analysis['shard_id']:04x})")
    print(f"  序列号 / Sequence: {analysis['sequence']:6d} (0x{analysis['sequence']:04x})")

    print(f"\n解读 / Interpretation:")
    print(f"  ✓ 视频在 / Video published at {result['datetime_utc']}")
    print(f"  ✓ 由分片/服务器 / Processed by shard/server #{analysis['shard_id']}")
    print(f"  ✓ 该秒内的序列号为 / Sequence number within that second is #{analysis['sequence']}")


if __name__ == "__main__":
    print("=" * 80)
    print("抖音 / TikTok 视频 ID 解密工具")
    print("Douyin / TikTok Video ID Decoder")
    print("作者 / Author: Evil0ctal")
    print("=" * 80)

    # ==================== 🔥 重点：算法验证 / Focus: Algorithm Validation ====================
    # 使用真实数据验证解码算法的准确性 / Validate decode algorithm accuracy using real data
    print("\n" + "🎯" * 40)
    print("使用 aweme_ids_output.json 进行算法验证")
    print("Using aweme_ids_output.json for algorithm validation")
    print("🎯" * 40)

    validate_decode_algorithm()

    # ==================== 其他功能演示 / Other Feature Demonstrations ====================
    # 示例输入（TikTok / 抖音视频ID）/ Sample input (TikTok / Douyin video IDs)
    sample_ids = [
        # Douyin aweme_ids and create_time
        "7153549929326120227",  # 1665565640
        "7266740902494833931",  # 1691919969
        "7196618597496524067",  # 1675593344
        # TikTok aweme_ids and create_time
        "7559684939684400414",  # 1760126333
        "7559661864628538654",  # 1760120961
        "7559607368695188766",  # 1760108270
    ]

    # 平台标签 / Platform labels
    platform_labels = [
        "Douyin-1", "Douyin-2", "Douyin-3",
        "TikTok-1", "TikTok-2", "TikTok-3"
    ]

    # 1. 基础解码 / Basic decoding
    print("\n=== 步骤1: 基础解码 / Step 1: Basic Decoding ===")
    batch_decode(sample_ids)

    # 2. 深度分析低32位结构 / Deep analysis of low 32-bit structure
    deep_analyze_low32(sample_ids)

    # 3. 统计分析 / Statistical analysis
    statistical_analysis(sample_ids, platform_labels)

    # 4. 可视化单个ID / Visualize a single ID
    # visualize_bit_structure(sample_ids[0])

    # 5. 示例：反向构造一个新ID / Example: Forge a new ID
    print("\n" + "=" * 80)
    print("=== 构造一枚自定义类抖音ID / Forge a Custom Douyin-style ID ===")
    print("=" * 80)
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    fake_id = forge_aweme_like_id(now_ts)
    print(f"当前UTC时间戳 / Current UTC timestamp: {now_ts}")
    print(f"伪造的ID / Forged ID: {fake_id}")
    print("\n验证解码结果 / Verify decoding result:")
    decoded_result = decode_aweme_id(str(fake_id), analyze_low32=True)
    for key, value in decoded_result.items():
        if key != "low32_analysis":
            print(f"  {key}: {value}")
        else:
            print(f"\n  低32位分析 / Low 32-bit analysis:")
            for scheme, data in value.items():
                print(f"    {scheme}: {data}")
