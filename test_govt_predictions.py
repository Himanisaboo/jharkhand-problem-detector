# -*- coding: utf-8 -*-
"""
Govt Route Verification Test Suite for Samadhan Setu
Tests 10 Government Route queries across English, Hindi, Hinglish, and Typos.
"""
import os
import sys

sys.path.append(r"c:\Users\Himani\Desktop\sih2026")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from predict_complaint import predict_complaint

govt_test_queries = [
    "Power outage in our area, urgent electricity supply restoration needed.",
    "हमारे क्षेत्र में बिजली कटौती, तत्काल बिजली आपूर्ति बहाल करने की आवश्यकता है।",
    "street light kaam nhi kar rhi power cut problem",
    "pwr outag in ur area urgnt electrcty suply restorsn neeeded",
    "Streetlight on main road is non-functional, causing safety issues.",
    "मुख्य सड़क पर स्ट्रीटलाइट काम नहीं कर रही है, सुरक्षा समस्याएं पैदा हो रही हैं।",
    "Severe water scarcity in our locality, immediate tanker or supply required.",
    "हमारे इलाके में पानी की भारी किल्लत, तुरंत टैंकर या सप्लाई की जरूरत है।",
    "Primary school teacher absenteeism and staff shortage in village school.",
    "गांव के स्कूल में प्राथमिक शिक्षक की अनुपस्थिति और कर्मचारियों की कमी।",
    "Handpump is broken and not drawing water, drinking water supply affected.",
    "हैंडपंप टूट गया है और पानी नहीं खींच रहा है, पीने के पानी की आपूर्ति प्रभावित हुई है।",
    "Distribution transformer burnt out in village, immediate replacement needed.",
    "गांव में वितरण ट्रांसफार्मर जल गया, तुरंत बदलने की जरूरत है।",
    "Local primary health center lacks doctor on duty and emergency ambulance.",
    "स्थानीय प्राथमिक स्वास्थ्य केंद्र में ड्यूटी पर डॉक्टर और आपातकालीन एम्बुलेंस की कमी है।",
    "PDS ration shop biometric fingerprint authentication failing repeatedly.",
    "पीडीएस राशन दुकान बायोमेट्रिक फिंगरप्रिंट प्रमाणीकरण बार-बार विफल हो रहा है।",
    "Road potholes causing severe traffic accidents in rainy season.",
    "बारिश के मौसम में सड़क के गड्ढों के कारण गंभीर सड़क दुर्घटनाएं हो रही हैं।",
    "Old age pension installment not credited for last 4 months.",
    "पिछले 4 महीने से वृद्धावस्था पेंशन की किस्त जमा नहीं हुई है।"
]

print("================ STARTING GOVERNMENT ROUTE VERIFICATION ================\n")
passed = 0
for idx, q in enumerate(govt_test_queries, 1):
    res = predict_complaint(q)
    results_dict = res.get("results", {})
    route = results_dict.get("route")
    officer = res.get("government_officer")
    unis = res.get("matched_institutions", [])
    
    # Verification criteria for Govt route:
    # 1. Route must be Government
    # 2. officer must be populated (not None)
    # 3. matched_institutions must be [] (empty)
    is_govt = (route == "Government")
    has_officer = (officer is not None and officer != {})
    no_uni = (len(unis) == 0)
    
    if is_govt and has_officer and no_uni:
        passed += 1
        status = "PASS"
    else:
        status = "FAIL"
        
    print(f"Test {idx:02d} [{status}]")
    print(f"  Input:        '{q}'")
    print(f"  Route:        {route}")
    print(f"  Officer:      {officer.get('primary_officer_name') if officer else None} ({officer.get('department_assigned') if officer else None})")
    print(f"  University:   {unis}")
    print("-" * 75)

print(f"\nResult: {passed}/{len(govt_test_queries)} Government test cases passed.")
