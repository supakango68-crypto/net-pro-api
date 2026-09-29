# main.py - CS2 Stats Tracker using Leetify API
from leetify_client import get_match_history, get_player_data


def get_player_profile(steam64_id: str):
    """
    ดึงข้อมูลโปรไฟล์ผู้เล่นจาก Leetify API
    """
    player = get_player_data(steam64_id)
    if not player:
        print("❌ ไม่พบข้อมูลผู้เล่น กรุณาตรวจ Steam ID / ลิงก์โปรไฟล์")
        return None

    print("=" * 60)
    print(f"👤 ชื่อผู้เล่น: {player.get('name', 'N/A')}")
    print(f"📊 จำนวนแมตช์ทั้งหมด: {player.get('totalMatches', 0)} แมตช์")
    print(f"🏆 อัตราชนะ: {player.get('winRate', 0):.2f}%")

    ranks = player.get("ranks") or {}
    if ranks.get("premier"):
        print(f"⭐ Premier Rank: {ranks['premier']}")
    if ranks.get("faceit"):
        print(f"🎮 FACEIT Level: {ranks['faceit']}")

    ratings = player.get("ratings") or {}
    print("\n--- 🎯 คะแนนทักษะ ---")
    print(f"  Aim (ความแม่นยำ): {ratings.get('aim', 'N/A')}")
    print(f"  Positioning (การวางตำแหน่ง): {ratings.get('positioning', 'N/A')}")
    print(f"  Utility (การใช้ระเบิด): {ratings.get('utility', 'N/A')}")
    print(f"  Clutch (การเผชิญหน้า): {ratings.get('clutch', 'N/A')}")
    print("=" * 60)
    return player


def show_recent_matches(steam64_id: str, limit: int = 5):
    """
    แสดงประวัติแมตช์ล่าสุดของผู้เล่น
    """
    matches = get_match_history(steam64_id, limit)
    if not matches:
        print("📭 ไม่พบประวัติแมตช์")
        return

    print(f"\n--- 🎮 ประวัติ {len(matches)} แมตช์ล่าสุด ---")
    print("-" * 60)

    for i, match in enumerate(matches, 1):
        result = "✅ ชนะ" if match.get("won", False) else "❌ แพ้"
        map_name = match.get("mapName", "Unknown")
        scores = match.get("teamScores", [])
        score_str = f"{scores[0]}-{scores[1]}" if len(scores) >= 2 else "N/A"
        started_at = match.get("startedAt", "")
        date_str = started_at[:16] if started_at else "N/A"
        print(f"{i}. แผนที่: {map_name} | {result} | สกอร์: {score_str}")
        print(f"   📅 {date_str}")
        print("-" * 40)


def compare_two_players(steam64_id_1: str, steam64_id_2: str):
    """
    เปรียบเทียบข้อมูลของผู้เล่น 2 คนแบบ side-by-side
    
    พารามิเตอร์:
        steam64_id_1: Steam ID ของผู้เล่นคนที่ 1
        steam64_id_2: Steam ID ของผู้เล่นคนที่ 2
    """
    print("\n⏳ กำลังดึงข้อมูลผู้เล่นคนที่ 1...")
    player1 = get_player_profile(steam64_id_1)
    
    print("\n⏳ กำลังดึงข้อมูลผู้เล่นคนที่ 2...")
    player2 = get_player_profile(steam64_id_2)
    
    if not player1 or not player2:
        print("❌ ไม่สามารถดึงข้อมูลผู้เล่นได้ กรุณาตรวจสอบ Steam ID")
        return
    
    print("\n" + "="*70)
    print("                 📊 เปรียบเทียบผู้เล่น")
    print("="*70)
    
    print(f"{'📌 หมวดหมู่':<20} | {player1.get('name', 'N/A'):<22} | {player2.get('name', 'N/A'):<22}")
    print("-" * 70)
    
    # ข้อมูลพื้นฐาน
    print(f"{'🏆 อัตราชนะ':<20} | {player1.get('winRate', 0):.1f}%{'':<18} | {player2.get('winRate', 0):.1f}%")
    print(f"{'🎯 จำนวนแมตช์':<20} | {player1.get('totalMatches', 0):<22} | {player2.get('totalMatches', 0):<22}")
    
    # คะแนนทักษะ
    print("\n" + "-" * 70)
    print("🎯 คะแนนทักษะ (0-100)")
    print("-" * 70)
    
    ratings1 = player1.get('ratings', {})
    ratings2 = player2.get('ratings', {})
    
    print(f"{'  Aim':<20} | {ratings1.get('aim', 'N/A'):<22} | {ratings2.get('aim', 'N/A'):<22}")
    print(f"{'  Positioning':<20} | {ratings1.get('positioning', 'N/A'):<22} | {ratings2.get('positioning', 'N/A'):<22}")
    print(f"{'  Utility':<20} | {ratings1.get('utility', 'N/A'):<22} | {ratings2.get('utility', 'N/A'):<22}")
    print(f"{'  Clutch':<20} | {ratings1.get('clutch', 'N/A'):<22} | {ratings2.get('clutch', 'N/A'):<22}")
    
    # สรุปผล
    print("\n" + "="*70)
    print("📝 สรุปจุดแข็ง-จุดอ่อน")
    print("="*70)
    
    categories = [
        ("Aim", ratings1.get('aim', 0), ratings2.get('aim', 0)),
        ("Positioning", ratings1.get('positioning', 0), ratings2.get('positioning', 0)),
        ("Utility", ratings1.get('utility', 0), ratings2.get('utility', 0)),
        ("Clutch", ratings1.get('clutch', 0), ratings2.get('clutch', 0))
    ]
    
    for name, score1, score2 in categories:
        if score1 and score2:
            if score1 > score2:
                print(f"✅ {name}: {player1.get('name', 'N/A')} เก่งกว่า ({score1} vs {score2})")
            elif score2 > score1:
                print(f"✅ {name}: {player2.get('name', 'N/A')} เก่งกว่า ({score2} vs {score1})")
            else:
                print(f"⚖️ {name}: ทั้งคู่เท่ากัน ({score1})")
        else:
            print(f"❌ {name}: ไม่มีข้อมูล")
    
    print("="*70)


def main():
    """
    เมนูหลักของโปรแกรม
    """
    while True:
        print("\n" + "="*60)
        print("      🎮 CS2 Stats Tracker & Comparison Tool")
        print("      ใช้ข้อมูลจาก Leetify API")
        print("="*60)
        print("\nเลือกสิ่งที่ต้องการทำ:")
        print("  1. ดูโปรไฟล์ผู้เล่น")
        print("  2. ดูประวัติแมตช์ล่าสุด")
        print("  3. เปรียบเทียบผู้เล่น 2 คน")
        print("  4. ออกจากโปรแกรม")
        
        choice = input("\n👉 กรุณาเลือก (1-4): ").strip()
        
        if choice == "1":
            steam_id = input("🔑 ป้อน Steam ID (ตัวเลข 17 หลัก): ").strip()
            if steam_id:
                get_player_profile(steam_id)
            else:
                print("❌ กรุณาป้อน Steam ID")
                
        elif choice == "2":
            steam_id = input("🔑 ป้อน Steam ID: ").strip()
            if steam_id:
                limit_input = input("📊 ต้องการดูกี่แมตช์? (กด Enter เพื่อใช้ 5): ").strip()
                limit = int(limit_input) if limit_input else 5
                show_recent_matches(steam_id, limit)
            else:
                print("❌ กรุณาป้อน Steam ID")
                
        elif choice == "3":
            id1 = input("🔑 Steam ID ผู้เล่นคนที่ 1: ").strip()
            id2 = input("🔑 Steam ID ผู้เล่นคนที่ 2: ").strip()
            if id1 and id2:
                compare_two_players(id1, id2)
            else:
                print("❌ กรุณาป้อน Steam ID ทั้งสองคน")
                
        elif choice == "4":
            print("👋 ขอบคุณที่ใช้งานโปรแกรม!")
            break
            
        else:
            print("❌ เลือกไม่ถูกต้อง กรุณาเลือก 1-4")
        
        input("\nกด Enter เพื่อกลับไปยังเมนูหลัก...")


if __name__ == "__main__":
    print("="*60)
    print("🚀 กำลังเริ่มโปรแกรม CS2 Stats Tracker...")
    print("="*60)
    main()