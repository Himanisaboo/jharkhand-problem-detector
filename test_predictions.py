import os
import sys

sys.path.append(r"c:\Users\Himani\Desktop\sih2026")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from predict_complaint import predict_complaint

test_queries = [
    # 1. Soil Moisture
    "मुझे एक soil moisture यंत्र चाहिए",
    "soil irrigation and soil moisture wale yantr mai",
    "i need soil moisture tool",
    "soil irigasion and soil moysture wale yantr BAU Ranchi",
    
    # 2. Soil Fertility Meter / NPK
    "hume mitti ki upjao pn dekhne ke liye yantr chahiye",
    "soil fertility testing meter device yantr required for farmers",
    "हमे मिट्टी की उपजाऊ पन देखने के लिए यंत्र चाहिए",
    
    # 3. Crop Disease AI
    "fasal me keeda lag gaya h AI leaf photo disease model chahiye",
    "crop disease attack leaf photo upload AI disease detection model",
    "पत्तियों की फोटो खींचकर फसल रोग बताने वाला AI मॉडल",
    
    # 4. Vernacular Speech AI
    "Santhali tribal language offline speech AI kiosk for primary school",
    "santhali bhasha me padhane ke liye offline speech AI kiosk",
    "संथाली जनजातीय भाषा में ऑफलाइन स्पीच AI कियोस्क प्राथमिक विद्यालय हेतु",
    
    # 5. IoT Flood Early Warning
    "ultrasonic river water level sensor array for flood early warning",
    "nadi me pani badhne par warning dene wala ultrasonic sensor array device",
    "बाढ़ पूर्व चेतावनी हेतु अल्ट्रासोनिक नदी जल स्तर सेंसर एरे",
    
    # 6. Solar Streetlight Microgrid Mesh Network
    "solar powered streetlight micro-controller mesh network design",
    "solar streetlight mesh network microcontroller device design",
    "सोलर स्ट्रीटलाइट माइक्रो-कंट्रोलर मेश नेटवर्क डिजाइन",
    
    # 7. Agri Drone Tech / Hilly Terrace Spraying
    "drone payload spraying for steep terrace farming in hilly areas",
    "pahad me terrace farming me dava chhidakne wala agri drone payload",
    "पहाड़ी इलाकों में सीढ़ीदार खेती हेतु ड्रोन पेलोड स्प्रेइंग सिस्टम",
    
    # 8. FinTech Hardware Dual Iris Scanner Kiosk
    "offline dual biometric iris scanner kiosk for worn fingerprints",
    "gise hue fingerprint ke liye iris scanner biometric kiosk machine",
    "घिसे हुए फingsरप्रिंट हेतु ऑफलाइन डुअल बायोमेट्रिक आईरिस स्कैनर कियोस्क"
]

print("================ INNOVATION PREDICTION VERIFICATION TEST ================\n")
all_passed = True
for idx, q in enumerate(test_queries, 1):
    res = predict_complaint(q)
    results = res["results"]
    matched_inst = res["matched_institutions"]
    inst_names = [inst["institution_name"] for inst in matched_inst] if matched_inst else []
    
    route = results["route"]
    cat = results["category"]
    dom = results["domain"]
    
    is_ok = (route == "Innovation")
    if not is_ok:
        all_passed = False
        
    status = "PASS" if is_ok else "FAIL"
    print(f"Test {idx:02d} [{status}]")
    print(f"  Input:        '{q}'")
    print(f"  Route:        {route}")
    print(f"  Domain:       {dom}")
    print(f"  Category:     {cat}")
    print(f"  University:   {inst_names}")
    print("-" * 75)

if all_passed:
    print("\nALL 22 INNOVATION TEST CASES PASSED PERFECTLY (100% Innovation Route Routing)!")
else:
    print("\nSome test cases failed classification.")
