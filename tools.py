def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Lead capture karta hai - assignment ka required tool.
    
    Real world mein ye CRM/database mein save karta.
    Abhi ke liye terminal pe print karta hai.
    """
    print("\n" + "=" * 55)
    print("🎯  LEAD CAPTURED SUCCESSFULLY!")
    print("=" * 55)
    print(f"  📛 Name     : {name}")
    print(f"  📧 Email    : {email}")
    print(f"  📱 Platform : {platform}")
    print("=" * 55)
    print("  ✅ Data sent to CRM (mock)")
    print("  ✅ Welcome email queued (mock)")
    print("=" * 55 + "\n")

    return f"Lead captured for {name} ({email}) - {platform} creator"
