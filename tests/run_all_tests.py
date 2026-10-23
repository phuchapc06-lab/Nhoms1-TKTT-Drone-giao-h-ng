"""
Trình chạy kiểm thử tự động toàn diện (Master Test Runner) cho Đề tài UDRP.
Phụ trách: Thành viên 5 (Nguyễn Phúc Hà - Tech Lead & System Integrator).
Tự động kích hoạt toàn bộ 13/13 bộ Unit Test và Integration Test độc lập của 6 thành viên.
"""
import os
import sys
import time
import subprocess

# Đảm bảo in tiếng Việt UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Danh sách 13 bộ kiểm thử độc lập
TEST_SUITES = [
    {
        "file": "tests/test_distance_matrix.py",
        "name": "TV2: A* Octile & Distance Matrix Cache",
        "member": "Thành viên 2"
    },
    {
        "file": "tests/test_ga.py",
        "name": "TV1: GA Core Engine & Hyperparameter Tuning",
        "member": "Thành viên 1"
    },
    {
        "file": "tests/test_energy_manager.py",
        "name": "TV3: Energy Manager & Charging Stations",
        "member": "Thành viên 3"
    },
    {
        "file": "tests/test_benchmark_generator.py",
        "name": "TV4: Multi-Scale Benchmark Generator",
        "member": "Thành viên 4"
    },
    {
        "file": "tests/test_member5.py",
        "name": "TV5: Multi-Objective Fitness & Visualizer",
        "member": "Thành viên 5 (Tech Lead)"
    },
    {
        "file": "tests/test_greedy_baseline.py",
        "name": "TV6: Baseline Greedy & 2-Opt Local Search",
        "member": "Thành viên 6"
    },
    {
        "file": "tests/test_day2_pipeline.py",
        "name": "E2E Pipeline Integration & Data Contract Validator",
        "member": "Tích hợp Nhóm (Ngày 2)"
    },
    {
        "file": "tests/test_day3_evaluator.py",
        "name": "Multi-Scale Benchmark Evaluator & Visual Charts",
        "member": "Tích hợp Nhóm (Ngày 3)"
    },
    {
        "file": "tests/test_day4_integration.py",
        "name": "Full System Integration (TV1 + TV2 + TV3 + TV6)",
        "member": "Tích hợp Toàn diện (Ngày 4)"
    },
    {
        "file": "tests/test_day5_integration.py",
        "name": "Hybrid GA Seeding & Dynamic Fleet Sizing",
        "member": "Tối ưu & Tinh chỉnh (Ngày 5)"
    },
    {
        "file": "tests/test_day1_parallel_ontime.py",
        "name": "TV5: Parallel Distance Matrix & On-time Delivery Rate",
        "member": "Tech Lead (Thứ Tư - 21/10)"
    },
    {
        "file": "tests/test_day2_benchmark_speedup.py",
        "name": "TV5: Multi-Scale Benchmark & Speedup Analysis",
        "member": "Tech Lead (Thứ Năm - 22/10)"
    },
    {
        "file": "tests/test_day3_complexity_correctness.py",
        "name": "TV5: Mathematical Correctness & Complexity Proofs",
        "member": "Tech Lead (Thứ Sáu - 23/10)"
    },
]

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("=" * 80)
    print("   HỆ THỐNG KIỂM THỬ HỒI QUY TỰ ĐỘNG TOÀN DỰ ÁN (MASTER TEST RUNNER)   ")
    print("   UAV Delivery Routing Problem (UDRP) - Nhóm 1 - Kiến trúc & Tích hợp  ")
    print("=" * 80)
    print(f"[*] Thư mục gốc dự án: {root_dir}")
    print(f"[*] Tổng số bộ kiểm thử: {len(TEST_SUITES)} suites\n")

    results = []
    total_start = time.time()

    for idx, suite in enumerate(TEST_SUITES, 1):
        rel_path = suite["file"]
        abs_path = os.path.join(root_dir, rel_path)
        title = suite["name"]
        member = suite["member"]

        print(f"[{idx:02d}/{len(TEST_SUITES):02d}] Đang chạy: {title} ({member})...", end=" ", flush=True)

        if not os.path.exists(abs_path):
            print("FAILED (File not found!)")
            results.append({"suite": title, "member": member, "status": "FILE_NOT_FOUND", "time": 0.0})
            continue

        start_t = time.time()
        res = subprocess.run(
            [sys.executable, abs_path],
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        elapsed = time.time() - start_t

        if res.returncode == 0:
            print(f"PASSED ({elapsed:.2f}s)")
            results.append({"suite": title, "member": member, "status": "PASSED", "time": elapsed})
        else:
            print(f"FAILED ({elapsed:.2f}s)")
            results.append({"suite": title, "member": member, "status": "FAILED", "time": elapsed, "output": res.stderr or res.stdout})

    total_time = time.time() - total_start
    passed_count = sum(1 for r in results if r["status"] == "PASSED")
    failed_count = len(results) - passed_count

    print("\n" + "=" * 80)
    print("                       BẢNG TỔNG HỢP KẾT QUẢ KIỂM THỬ                   ")
    print("=" * 80)
    print(f"{'STT':<4} | {'Bộ Kiểm Thử / Chức Năng':<45} | {'Phụ Trách':<20} | {'Kết Quả':<8} | {'Thời Gian':<9}")
    print("-" * 94)

    for idx, r in enumerate(results, 1):
        status_str = "PASS" if r["status"] == "PASSED" else "FAIL"
        print(f"{idx:<4} | {r['suite']:<45} | {r['member']:<20} | {status_str:<8} | {r['time']:.2f}s")

    print("-" * 94)
    print(f"TỔNG KẾT: {passed_count}/{len(results)} SUITES PASSED ({passed_count / len(results) * 100:.1f}%) - Tổng thời gian: {total_time:.2f}s")

    if failed_count > 0:
        print("\n[!] CẢNH BÁO: CÓ BỘ KIỂM THỬ THẤT BẠI:")
        for r in results:
            if r["status"] != "PASSED":
                print(f"  - {r['suite']} ({r['member']}): {r['status']}")
                if "output" in r:
                    print(f"    Chi tiết: {r['output'][:300]}...")
        print("=" * 80)
        sys.exit(1)
    else:
        print(f"🎉 TẤT CẢ {passed_count}/{len(results)} BỘ KIỂM THỬ ĐÃ VƯỢT QUA 100% XUẤT SẮC!")
        print("=" * 80)
        sys.exit(0)

if __name__ == "__main__":
    main()
