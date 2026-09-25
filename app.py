import os
import sys
import sqlite3
import pandas as pd
from flask import Flask, render_template_string, request, jsonify

# Import updated inference module
from predict_complaint import (
    predict_complaint,
    load_pipeline,
    load_institution_db,
    load_taxonomy_db,
    SOLUTION_REUSE_CORPUS
)

app = Flask(__name__)

DATA_DIR = r"c:\Users\Himani\Desktop\sih2026"
DB_PATH = os.path.join(DATA_DIR, "samadhan_setu.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE,
        complaint_text TEXT NOT NULL,
        proof_filename TEXT NOT NULL,
        gps_location TEXT,
        domain TEXT,
        category TEXT,
        route TEXT,
        severity TEXT,
        priority_score INTEGER,
        status TEXT,
        dept_assigned TEXT,
        officer_name TEXT,
        escalation_officer TEXT,
        assigned_university TEXT,
        backup_university TEXT,
        university_task TEXT,
        university_status TEXT DEFAULT 'PENDING_DECISION',
        prototype_title TEXT DEFAULT 'N/A',
        prototype_demo_link TEXT DEFAULT 'N/A',
        prototype_description TEXT DEFAULT 'N/A',
        prototype_status TEXT DEFAULT 'NOT_SUBMITTED',
        reward_granted TEXT DEFAULT 'NONE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("""
        INSERT INTO complaints (
            ticket_id, complaint_text, proof_filename, gps_location,
            domain, category, route, severity, priority_score, status,
            dept_assigned, officer_name, escalation_officer,
            assigned_university, backup_university, university_task, university_status
        ) VALUES 
        (
            'SS-1001', 'soil irrigation and soil moisture wale yantr mai', 'soil_moisture_geotagged.jpg', 'Kanke Ward 2, Ranchi',
            'Agriculture & Crop Management', 'Lack of Soil Testing & Low Fertility', 'Innovation', 'High', 92, 'GOVT_VERIFIED',
            'N/A', 'N/A', 'N/A',
            'Birsa Agricultural University (BAU), Ranchi', 'BIT Mesra, Ranchi', 'Design low-cost solar-powered IoT soil moisture sensor node & NPK testing kit for Jharkhand farmers.', 'ACCEPTED_IN_PROGRESS'
        ),
        (
            'SS-1002', 'fasal me keeda lag gaya h AI leaf photo disease model chahiye', 'crop_pest_leaf_photo.jpg', 'Namkum Block, Ranchi',
            'Agriculture & Crop Management', 'Pest Attacks & Crop Disease Outbreak', 'Innovation', 'High', 88, 'GOVT_VERIFIED',
            'N/A', 'N/A', 'N/A',
            'BIT Mesra, Ranchi', 'Birsa Agricultural University (BAU), Ranchi', 'Deploy Mobile Computer Vision AI for real-time leaf photo pest & crop disease diagnosis.', 'ACCEPTED_IN_PROGRESS'
        )
        """)
    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------------------------
# FULL SIH 2026 SAMADHAN SETU PLATFORM FRONTEND (LIGHT THEME HTML)
# -------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samadhan Setu — AI Civic Intelligence & Routing Platform</title>
    <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
    <style>
        .gradient-brand { background: linear-gradient(135deg, #2563eb 0%, #4f46e5 50%, #7c3aed 100%); }
        .pulse-live { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen font-sans antialiased selection:bg-indigo-500 selection:text-white">

    <!-- Top Navigation Header -->
    <header class="border-b border-slate-200 bg-white/95 backdrop-blur sticky top-0 z-50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl gradient-brand flex items-center justify-center font-black text-white shadow-md text-lg">
                    SS
                </div>
                <div>
                    <h1 class="text-lg font-black text-slate-900 tracking-wide flex items-center space-x-2">
                        <span>SAMADHAN SETU</span>
                        <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">Master Platform</span>
                    </h1>
                    <p class="text-xs text-slate-500">AI-Powered Societal Problem Routing & Resolution Platform for Jharkhand</p>
                </div>
            </div>
            
            <!-- Navigation Tabs -->
            <div class="flex space-x-1 sm:space-x-2 text-xs font-semibold overflow-x-auto py-2">
                <button onclick="switchTab('submit-tab')" id="nav-submit" class="px-3.5 py-2 rounded-xl bg-indigo-600 text-white shadow-md transition flex items-center space-x-1.5">
                    <span>📍</span> <span>Citizen Portal & AI Engine</span>
                </button>
                <button onclick="switchTab('escalation-tab')" id="nav-escalation" class="px-3.5 py-2 rounded-xl bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition flex items-center space-x-1.5">
                    <span>🏛️</span> <span>Govt Officer Portal</span>
                    <span id="badge-govt-pending" class="px-1.5 py-0.5 rounded-full text-[9px] bg-amber-500 text-white font-black">0 Pending</span>
                </button>
                <button onclick="switchTab('innovation-tab')" id="nav-innovation" class="px-3.5 py-2 rounded-xl bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition flex items-center space-x-1.5">
                    <span>🎓</span> <span>University R&D Portal</span>
                    <span id="badge-uni-count" class="px-1.5 py-0.5 rounded-full text-[9px] bg-purple-600 text-white font-black">0 Allotted</span>
                </button>
                <button onclick="switchTab('leaderboard-tab')" id="nav-leaderboard" class="px-3.5 py-2 rounded-xl bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition flex items-center space-x-1.5">
                    <span>🏆</span> <span>Impact & Live Tracking</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content Body -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        <!-- =================================================================== -->
        <!-- TAB 1: CITIZEN PORTAL & REAL-TIME AI PIPELINE -->
        <!-- =================================================================== -->
        <div id="submit-tab" class="tab-content space-y-8">
            
            <!-- Hero Banner & Value Proposition -->
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm relative overflow-hidden">
                <div class="relative z-10">
                    <span class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold mb-3">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 pulse-live"></span>
                        <span>Complete Connected Pipeline: Citizen ➔ AI Routing ➔ Govt Officer Audit ➔ University R&D Prototype ➔ State Reward</span>
                    </span>
                    <h2 class="text-2xl font-extrabold text-slate-900">AI Societal Problem Intelligence Engine</h2>
                    <p class="text-slate-600 text-sm max-w-4xl mt-1 leading-relaxed">
                        Submit societal problems with <strong>mandatory photo proof</strong>. Route is classified automatically. Assigned Officers & Universities are displayed clearly. Universities submit working prototypes for Govt audit & state R&D reward grants!
                    </p>
                    
                    <!-- Presets Chips -->
                    <div class="mt-4 flex flex-wrap items-center gap-2 text-xs">
                        <span class="text-slate-500 font-semibold">Test Presets:</span>
                        <button onclick="setSample('मुझे एक soil moisture यंत्र चाहिए')" class="px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl font-bold transition">
                            🌾 मुझे एक soil moisture यंत्र चाहिए (Innovation Route)
                        </button>
                        <button onclick="setSample('हमारे यहां लाइट नहीं आ रही है')" class="px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 rounded-xl font-bold transition">
                            ⚡ हमारे यहां लाइट नहीं आ रही है (Govt Route)
                        </button>
                        <button onclick="setSample('street light kaam nhi kr rhi')" class="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-300 rounded-xl font-bold transition">
                            🛣️ street light kaam nhi kr rhi (Govt Route)
                        </button>
                    </div>
                </div>
            </div>

            <!-- Input & Pipeline Split Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
                
                <!-- Left Input Form (5 cols) -->
                <div class="lg:col-span-5 bg-white border border-slate-200 rounded-3xl p-6 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
                                <span>📝</span> <span>Citizen Grievance Submission</span>
                            </h3>
                            <span class="text-[10px] text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200 font-bold">Proof Mandatory</span>
                        </div>

                        <!-- Voice-First Input Module -->
                        <div class="mb-4 p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
                            <div class="flex items-center justify-between mb-2">
                                <span class="text-xs font-bold text-slate-700 flex items-center space-x-1.5">
                                    <span>🎤</span> <span>Regional Voice Input (W3C Speech API)</span>
                                </span>
                                <select id="voice-lang" class="bg-white border border-slate-300 rounded text-[10px] px-2 py-0.5 text-slate-700">
                                    <option value="hi-IN">Hindi (हिन्दी)</option>
                                    <option value="sat-IN">Santhali (संथाली)</option>
                                    <option value="nag-IN">Nagpuri (नागपुरी)</option>
                                    <option value="en-IN">Hinglish / English</option>
                                </select>
                            </div>
                            <button type="button" onclick="toggleVoiceRecording()" id="voice-btn" class="w-full py-2 bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-300 rounded-xl text-xs font-bold transition flex items-center justify-center space-x-2 shadow-sm">
                                <span id="mic-icon">🔴</span> <span id="voice-status-text">Click to speak in your regional language...</span>
                            </button>
                        </div>

                        <form id="complaint-form" onsubmit="handleFormSubmit(event)" class="space-y-4">
                            <div>
                                <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Problem Description / Grievance Statement</label>
                                <textarea id="complaint_text" rows="4" required
                                    class="w-full bg-white border border-slate-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-2xl p-3.5 text-slate-900 text-sm placeholder-slate-400 transition"
                                    placeholder="Type or speak problem details in English, Hindi, Hinglish, short or messy words..."></textarea>
                            </div>

                            <!-- Photo / Video Proof Dropzone Module (MANDATORY) -->
                            <div class="p-4 bg-slate-50 border border-dashed border-rose-300 rounded-2xl">
                                <div class="flex items-center justify-between mb-2">
                                    <label class="text-xs font-bold text-slate-800 flex items-center space-x-1">
                                        <span>📸</span> <span>Geo-Tagged Photo / Video Proof</span>
                                        <span class="text-rose-600 font-bold">*REQUIRED</span>
                                    </label>
                                    <span class="text-[10px] text-slate-500">Auto GPS Tagged</span>
                                </div>
                                <input type="file" id="proof_file" accept="image/*,video/*" onchange="handleProofUpload(event)" class="hidden">
                                <label for="proof_file" id="proof-label-box" class="cursor-pointer block text-center py-3 px-4 bg-white border border-rose-200 rounded-xl hover:border-rose-400 transition">
                                    <span class="text-xs text-rose-700 font-bold block">📁 Upload Photo Proof (Mandatory for Action)</span>
                                    <span class="text-[10px] text-slate-400">Supports JPG, PNG, MP4</span>
                                </label>
                                
                                <div id="proof-preview-container" class="mt-3 hidden p-2 bg-white rounded-xl border border-slate-200 flex items-center space-x-3">
                                    <div class="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center text-xl overflow-hidden border border-slate-200" id="proof-thumb">
                                        🖼️
                                    </div>
                                    <div class="flex-1 text-xs overflow-hidden">
                                        <p id="proof-filename" class="font-bold text-slate-900 truncate">photo_proof.jpg</p>
                                        <p class="text-[10px] text-emerald-600 font-bold flex items-center space-x-1">
                                            <span>📍 GPS: 23.3441° N, 85.3090° E</span>
                                            <span>(Ranchi, JH)</span>
                                        </p>
                                    </div>
                                    <span class="text-[10px] px-2 py-0.5 bg-emerald-50 text-emerald-700 font-bold rounded border border-emerald-200">Proof Attached</span>
                                </div>
                            </div>

                            <!-- Error Box for Missing Proof -->
                            <div id="proof-error-box" class="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold rounded-xl hidden">
                                ⚠️ Photo/Video proof is MANDATORY! Please upload photo proof to submit grievance.
                            </div>

                            <button type="submit" id="submit-btn" class="w-full py-3.5 gradient-brand text-white rounded-2xl font-bold shadow-md hover:opacity-95 transition flex items-center justify-center space-x-2 text-sm">
                                <span>🚀 Route via AI Pipeline & Save to DB</span>
                            </button>
                        </form>
                    </div>

                    <!-- Live Pipeline Status Banner -->
                    <div id="status-banner" class="mt-4 p-3 rounded-2xl text-xs flex items-center space-x-3 hidden bg-indigo-50 border border-indigo-200 text-indigo-900">
                        <div class="w-2.5 h-2.5 rounded-full bg-indigo-600 pulse-live"></div>
                        <span id="status-text">Saving ticket to database & executing AI routing...</span>
                    </div>
                </div>

                <!-- Right Real-Time AI Pipeline Output (7 cols) -->
                <div class="lg:col-span-7 space-y-6">
                    
                    <!-- AI Prediction Card -->
                    <div id="prediction-card" class="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-6 hidden">
                        
                        <!-- Header & Badges -->
                        <div class="flex items-start justify-between pb-4 border-b border-slate-100">
                            <div>
                                <div class="flex items-center space-x-2 mb-1">
                                    <span id="res-ticket-id" class="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-slate-100 text-slate-800 border border-slate-300">
                                        Ticket #SS-1001
                                    </span>
                                    <span id="res-route-badge" class="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider">
                                        Route
                                    </span>
                                </div>
                                <h3 id="res-category" class="text-xl font-extrabold text-slate-900">Category</h3>
                                <p id="res-domain" class="text-xs text-slate-500 mt-0.5">Domain</p>
                            </div>
                            <div class="text-right">
                                <span class="text-xs text-slate-400 block font-semibold">Priority Score</span>
                                <span id="res-score" class="text-2xl font-black text-indigo-600">--/100</span>
                            </div>
                        </div>

                        <!-- Verification Alert Status Banner -->
                        <div id="verification-notice-banner" class="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start space-x-3">
                            <span class="text-xl">⏳</span>
                            <div>
                                <p class="font-bold">Status: Pending Govt Nodal Officer Proof Verification</p>
                                <p class="text-amber-700 text-[11px] mt-0.5">
                                    Grievance & photo proof saved in database! Govt Nodal Officer in <strong>Tab 2</strong> will inspect photo proof. Once verified, official allotment will activate.
                                </p>
                            </div>
                        </div>

                        <!-- 5-Step Connected Progress Audit Bar -->
                        <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
                            <span class="text-xs font-bold text-slate-700 block">📍 Ticket Connected Audit Trail (Saved in Database)</span>
                            <div class="grid grid-cols-5 gap-1.5 text-center text-[10px] font-bold">
                                <div class="p-1.5 rounded bg-indigo-600 text-white shadow-sm">1. Proof Submitted</div>
                                <div class="p-1.5 rounded bg-indigo-600 text-white shadow-sm">2. Saved in DB</div>
                                <div id="step-3-badge" class="p-1.5 rounded bg-amber-100 text-amber-800 border border-amber-300">3. Govt Verification</div>
                                <div id="step-4-badge" class="p-1.5 rounded bg-slate-200 text-slate-600">4. Allotment Active</div>
                                <div id="step-5-badge" class="p-1.5 rounded bg-slate-200 text-slate-600">5. Citizen Sign-off</div>
                            </div>
                        </div>

                        <!-- Allotted Govt Officer Details Card (Shown ONLY for Government & Hybrid Routes) -->
                        <div id="govt-officer-wrapper" class="p-4 bg-blue-50 border border-blue-200 rounded-2xl space-y-2 hidden">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-blue-900 flex items-center space-x-1">
                                    <span>🏛️</span> <span>Allotted Government Department & Nodal Officer</span>
                                </span>
                                <span id="sla-timer-tag" class="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded border border-blue-300">Target SLA: 24 Hours</span>
                            </div>
                            <div class="text-xs text-slate-700 space-y-1">
                                <p><strong>Department:</strong> <span id="govt-dept">Department of Urban / Rural Development</span></p>
                                <p><strong>Primary Nodal Officer:</strong> <span id="govt-officer-name">Er. Alok Kumar Verma</span> (Executive Engineer)</p>
                                <p><strong>Contact:</strong> <span id="govt-contact">+91 94311 02847 | nodal.ranchi@jharkhand.gov.in</span></p>
                                <p class="text-[11px] text-rose-700 font-bold mt-1 bg-white p-2 rounded border border-rose-200">
                                    ⚠️ Auto-Escalation Target: <span id="govt-escalation">Shri Rahul Sharma, IAS (District Collector DC Ranchi)</span> if unresolved within SLA.
                                </p>
                            </div>
                        </div>

                        <!-- Single Best Matched University R&D Partner (Shown ONLY for Innovation & Hybrid Routes) -->
                        <div id="hei-section-wrapper" class="p-4 bg-purple-50 border border-purple-200 rounded-2xl space-y-3 hidden">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-purple-900 flex items-center space-x-1">
                                    <span>🎓</span> <span>Allotted University R&D Innovation Partner</span>
                                </span>
                                <span class="text-[10px] px-2 py-0.5 bg-purple-100 text-purple-800 font-bold rounded border border-purple-300">Top 1 Primary Match</span>
                            </div>
                            <div id="single-hei-card" class="bg-white p-4 rounded-xl border border-purple-200 space-y-2">
                                <!-- Dynamic single HEI item inserted by JS -->
                            </div>
                        </div>

                        <!-- Citizen Confirmation / Feedback Box -->
                        <div class="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-3">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-slate-900">Citizen Sign-Off & Resolution Verification</span>
                                <span id="proof-status-badge" class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                                    Pending Govt Proof Verification
                                </span>
                            </div>
                            <p class="text-xs text-slate-500">
                                Once the officer or university deploys the solution, click below to confirm resolution or trigger immediate Tier-2 District Magistrate escalation.
                            </p>
                            <div class="flex space-x-2">
                                <button onclick="verifyResolution(true)" class="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-sm">
                                    ✔ Confirm Resolved
                                </button>
                                <button onclick="verifyResolution(false)" class="flex-1 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition shadow-sm">
                                    ✖ Reject & Escalate to DC
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Placeholder empty state -->
                    <div id="placeholder-card" class="bg-white border border-slate-200 rounded-3xl p-12 text-center shadow-sm space-y-3">
                        <div class="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-3xl mx-auto">
                            🤖
                        </div>
                        <h3 class="text-base font-bold text-slate-800">Awaiting Citizen Grievance & Photo Proof</h3>
                        <p class="text-xs text-slate-500 max-w-sm mx-auto">
                            Upload mandatory photo proof & type/speak your complaint to save in database and trigger Govt verification.
                        </p>
                    </div>

                    <!-- Citizen Registered History List (Loaded from Database) -->
                    <div class="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
                        <h3 class="text-sm font-bold text-slate-900 flex items-center justify-between">
                            <span>📋 Citizen Saved Grievances</span>
                            <span class="text-[10px] text-emerald-600 font-bold">Persistent Across Refresh</span>
                        </h3>
                        <div id="grievance-history-list" class="space-y-3 text-xs">
                            <p class="text-slate-400 text-xs">Loading database records...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="escalation-tab" class="tab-content hidden space-y-8">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div>
                    <h2 class="text-2xl font-extrabold text-slate-900">🏛️ Central Government Nodal Audit & Multi-Department Portal</h2>
                    <p class="text-slate-600 text-sm mt-1">Automated Multi-Department Grievance Intelligence — Complaints auto-routed to respective Department Nodal Officers (Electricity, PHED, PWD, Education, Health, PDS, etc.) and Central DC Office.</p>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="text-xs font-bold text-slate-500">Filter Dept:</span>
                    <select id="govt-dept-filter" onchange="loadSavedComplaintsFromDB()" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 font-bold focus:ring-1 focus:ring-indigo-500 shadow-sm">
                        <option value="ALL">🏢 All Departments (Central State Feed)</option>
                        <option value="Energy">⚡ Dept of Energy & Power Supply</option>
                        <option value="PHED">💧 Dept of Public Health Engineering (PHED Water)</option>
                        <option value="PWD">🛣️ Dept of Public Works (PWD & Roads)</option>
                        <option value="Education">🎓 Dept of School Education & Literacy</option>
                        <option value="Health">🏥 Dept of Health & Medical Services</option>
                        <option value="Food">🌾 Dept of Food & PDS Security</option>
                        <option value="Agriculture">🚜 Dept of Agriculture & Animal Husbandry</option>
                        <option value="Urban">🏙️ Dept of Urban Development (RMC)</option>
                        <option value="Social">👵 Dept of Social Security & Pensions</option>
                    </select>
                </div>
            </div>

            <!-- SECTION 1: Priority Complaints Queue for Proof Verification -->
            <div class="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-6">
                <div class="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
                        <span>🚨</span> <span>Grievance Proof Verification Queue</span>
                    </h3>
                    <span class="text-xs text-slate-500 font-semibold">Sorted by Priority Score</span>
                </div>

                <div id="govt-queue-container" class="space-y-4">
                    <p class="text-slate-400 text-xs">Loading pending verification queue from database...</p>
                </div>
            </div>

            <!-- SECTION 2: University R&D Prototype Audit & State Reward Desk -->
            <div class="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-6">
                <div class="flex items-center justify-between border-b border-slate-100 pb-4">
                    <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
                        <span>🔬</span> <span>University R&D Prototype Audit & State Grant Reward Desk</span>
                    </h3>
                    <span class="px-2.5 py-0.5 rounded bg-purple-100 text-purple-800 text-xs font-bold border border-purple-200">State R&D Grant ₹5,00,000 Award Desk</span>
                </div>

                <div id="govt-prototype-audit-container" class="space-y-4">
                    <p class="text-slate-400 text-xs">Loading submitted prototypes for Govt audit...</p>
                </div>
            </div>
        </div>

        <!-- =================================================================== -->
        <!-- TAB 3: UNIVERSITY & RESEARCH PORTAL (PROTOTYPE UPLOAD & REWARD HUB) -->
        <!-- =================================================================== -->
        <div id="innovation-tab" class="tab-content hidden space-y-8">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex items-center justify-between">
                <div>
                    <h2 class="text-2xl font-extrabold text-slate-900">🎓 University & Research Portal (Prototype Upload & Reward Hub)</h2>
                    <p class="text-slate-600 text-sm mt-1">Accept allotted problems, build working prototypes, and submit prototype proof to Govt Officers for State R&D Rewards (₹5,00,000).</p>
                </div>
                <button onclick="loadInstitutions()" class="px-3.5 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-xs font-bold transition">
                    🔄 Refresh HEI Database
                </button>
            </div>

            <!-- Allotted Problems per University Grid -->
            <div class="space-y-6">
                <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
                    <span>🏛️</span> <span>Jharkhand Universities & Assigned R&D Problems (Prototype Submission Desk)</span>
                </h3>

                <!-- Active Allotted Tasks List Container -->
                <div id="university-allotted-tasks-container" class="space-y-4">
                    <p class="text-xs text-slate-500">Loading university allotted tasks...</p>
                </div>

                <!-- HEI Database Cards Grid -->
                <div id="institution-cards-grid" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Loaded dynamically via /api/institutions -->
                </div>
            </div>
        </div>

        <!-- =================================================================== -->
        <!-- TAB 4: IMPACT & LIVE TICKET TRACKING LEADERBOARD -->
        <!-- =================================================================== -->
        <div id="leaderboard-tab" class="tab-content hidden space-y-8">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex items-center justify-between">
                <div>
                    <h2 class="text-2xl font-extrabold text-slate-900">🏆 Impact Analytics & Database Ticket Search</h2>
                    <p class="text-slate-600 text-sm mt-1">Statewide resolution impact, district performance rankings, and universal ticket tracking search.</p>
                </div>
                <span class="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold rounded-xl">
                    Live Governance Feed
                </span>
            </div>

            <!-- Statewide KPI Metrics Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm space-y-1">
                    <span class="text-xs font-semibold text-slate-500">Total Grievances Processed</span>
                    <p id="kpi-total-count" class="text-3xl font-black text-slate-900">4,054</p>
                    <span class="text-[10px] text-emerald-600 font-bold">↑ 100% Persistent System Feed</span>
                </div>
                <div class="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm space-y-1">
                    <span class="text-xs font-semibold text-slate-500">Govt SLA Resolution Rate</span>
                    <p class="text-3xl font-black text-emerald-600">94.8%</p>
                    <span class="text-[10px] text-slate-400 font-semibold">Avg SLA Time: 18.2 Hours</span>
                </div>
                <div class="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm space-y-1">
                    <span class="text-xs font-semibold text-slate-500">University R&D Projects</span>
                    <p id="kpi-uni-count" class="text-3xl font-black text-purple-600">38</p>
                    <span class="text-[10px] text-purple-600 font-bold">Single Best University Match</span>
                </div>
                <div class="bg-white border border-slate-200 rounded-3xl p-5 shadow-sm space-y-1">
                    <span class="text-xs font-semibold text-slate-500">State R&D Grants Issued</span>
                    <p id="kpi-grant-count" class="text-3xl font-black text-amber-600">₹1.9 Crore</p>
                    <span class="text-[10px] text-amber-600 font-bold">₹5,00,000 per Approved Prototype</span>
                </div>
            </div>

            <!-- Universal Ticket ID Search & Live Audit Trail -->
            <div class="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
                <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
                    <span>🔍</span> <span>Universal Ticket Search & Live Step-by-Step Tracking</span>
                </h3>
                <div class="flex space-x-3">
                    <input type="text" id="ticket-search-input" value="SS-1001" placeholder="Enter Ticket ID (e.g. SS-1001)" class="flex-1 border border-slate-300 rounded-xl px-4 py-2.5 text-xs text-slate-900 font-mono focus:ring-1 focus:ring-indigo-500">
                    <button onclick="searchTicketProgress()" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition">
                        Search Database Trail
                    </button>
                </div>

                <div id="ticket-search-result" class="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-200 pb-3 text-xs">
                        <div>
                            <span id="search-ticket-title" class="font-bold text-slate-900 font-mono text-sm">Ticket ID: SS-1001</span>
                            <p id="search-problem-text" class="text-slate-500 mt-0.5">Problem: <strong>"street light kaam nhi kr rhi"</strong></p>
                        </div>
                        <span id="search-current-status" class="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
                            Pending Govt Verification
                        </span>
                    </div>

                    <!-- Visual Timeline -->
                    <div class="space-y-3 text-xs">
                        <div class="flex items-start space-x-3">
                            <span class="w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-[10px]">1</span>
                            <div>
                                <p class="font-bold text-slate-900">Proof Uploaded & Saved to System Database</p>
                                <p class="text-[10px] text-slate-500">Photo Proof Verified | Geotagged Ranchi</p>
                            </div>
                        </div>
                        <div class="flex items-start space-x-3">
                            <span class="w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-[10px]">2</span>
                            <div>
                                <p class="font-bold text-slate-900">AI Routing Engine Executed</p>
                                <p id="search-route-info" class="text-[10px] text-slate-500">Route: Government | Domain: Roads & Mobility</p>
                            </div>
                        </div>
                        <div class="flex items-start space-x-3">
                            <span id="timeline-node-3" class="w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center font-bold text-[10px]">3</span>
                            <div>
                                <p id="timeline-text-3" class="font-bold text-slate-900">Govt Officer Proof Verification & Order Approval</p>
                                <p id="timeline-subtext-3" class="text-[10px] text-amber-700">Awaiting Nodal Officer Signature in Tab 2</p>
                            </div>
                        </div>
                        <div class="flex items-start space-x-3">
                            <span id="timeline-node-4" class="w-6 h-6 rounded-full bg-slate-300 text-slate-600 flex items-center justify-center font-bold text-[10px]">4</span>
                            <div>
                                <p id="timeline-text-4" class="font-bold text-slate-400">Allotment Active & Prototype Development</p>
                                <p id="timeline-subtext-4" class="text-[10px] text-slate-400">Pending Govt Verification</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- District Performance Leaderboard Table -->
            <div class="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
                <h3 class="text-base font-bold text-slate-900 flex items-center space-x-2">
                    <span>📊</span> <span>Jharkhand District Governance & SLA Compliance Leaderboard</span>
                </h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[10px]">
                            <tr>
                                <th class="p-3">Rank</th>
                                <th class="p-3">District</th>
                                <th class="p-3">Total Complaints</th>
                                <th class="p-3">Resolved Within SLA</th>
                                <th class="p-3">SLA Compliance Rate</th>
                                <th class="p-3">Status</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 text-slate-700">
                            <tr class="hover:bg-slate-50">
                                <td class="p-3 font-bold text-indigo-600">#1</td>
                                <td class="p-3 font-bold text-slate-900">Ranchi</td>
                                <td class="p-3">1,240</td>
                                <td class="p-3">1,192</td>
                                <td class="p-3 font-bold text-emerald-600">96.1%</td>
                                <td class="p-3"><span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">Top Performing</span></td>
                            </tr>
                            <tr class="hover:bg-slate-50">
                                <td class="p-3 font-bold text-indigo-600">#2</td>
                                <td class="p-3 font-bold text-slate-900">Dhanbad</td>
                                <td class="p-3">890</td>
                                <td class="p-3">842</td>
                                <td class="p-3 font-bold text-emerald-600">94.6%</td>
                                <td class="p-3"><span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">Excellent</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </main>

    <!-- Interactive Client JS Logic -->
    <script>
        let isRecording = false;
        let recognition = null;
        let attachedProofFile = null;
        let currentActiveTicket = null;

        document.addEventListener('DOMContentLoaded', () => {
            loadSavedComplaintsFromDB();
        });

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById(tabId).classList.remove('hidden');

            ['submit', 'escalation', 'innovation', 'leaderboard'].forEach(t => {
                const btn = document.getElementById('nav-' + t);
                if (t + '-tab' === tabId) {
                    btn.className = "px-3.5 py-2 rounded-xl bg-indigo-600 text-white shadow-md transition flex items-center space-x-1.5";
                } else {
                    btn.className = "px-3.5 py-2 rounded-xl bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition flex items-center space-x-1.5";
                }
            });

            if (tabId === 'innovation-tab') {
                loadInstitutions();
            }
        }

        function setSample(text) {
            document.getElementById('complaint_text').value = text;
            attachedProofFile = { name: "sample_proof_geotagged.jpg", size: 1048576 };
            document.getElementById('proof-preview-container').classList.remove('hidden');
            document.getElementById('proof-filename').innerText = attachedProofFile.name + " (1.0 MB)";
            document.getElementById('proof-error-box').classList.add('hidden');
            
            const event = new Event('submit', { cancelable: true });
            document.getElementById('complaint-form').dispatchEvent(event);
        }

        function toggleVoiceRecording() {
            const btnText = document.getElementById('voice-status-text');
            const micIcon = document.getElementById('mic-icon');
            const lang = document.getElementById('voice-lang').value;

            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert("Speech recognition is not supported in this browser. Please use Chrome/Edge.");
                return;
            }

            if (!isRecording) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.lang = lang;
                recognition.interimResults = false;

                recognition.onstart = function() {
                    isRecording = true;
                    micIcon.innerText = "🎙️";
                    btnText.innerText = "Listening... Speak your complaint now...";
                };

                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('complaint_text').value = transcript;
                };

                recognition.onerror = function() {
                    isRecording = false;
                    micIcon.innerText = "🔴";
                    btnText.innerText = "Voice input error. Click to try again.";
                };

                recognition.onend = function() {
                    isRecording = false;
                    micIcon.innerText = "🔴";
                    btnText.innerText = "Click to speak in your regional language...";
                };

                recognition.start();
            } else {
                if (recognition) recognition.stop();
            }
        }

        function handleProofUpload(e) {
            const file = e.target.files[0];
            if (file) {
                attachedProofFile = file;
                document.getElementById('proof-preview-container').classList.remove('hidden');
                document.getElementById('proof-filename').innerText = file.name + ` (${(file.size/1024).toFixed(1)} KB)`;
                document.getElementById('proof-error-box').classList.add('hidden');
            }
        }

        async function handleFormSubmit(e) {
            e.preventDefault();
            const text = document.getElementById('complaint_text').value;
            if (!text.trim()) return;

            if (!attachedProofFile) {
                document.getElementById('proof-error-box').classList.remove('hidden');
                alert("⚠️ Photo/Video proof is MANDATORY to submit a grievance! Please click 'Upload Photo Proof'.");
                return;
            }

            const banner = document.getElementById('status-banner');
            banner.classList.remove('hidden');

            document.getElementById('placeholder-card').classList.add('hidden');
            document.getElementById('prediction-card').classList.add('hidden');

            try {
                const res = await fetch('/api/complaint/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        complaint_text: text,
                        proof_filename: attachedProofFile.name,
                        gps_location: "23.3441° N, 85.3090° E (Ranchi, JH)"
                    })
                });

                const data = await res.json();
                banner.classList.add('hidden');
                
                if (data.error) {
                    alert("Error: " + data.error);
                    return;
                }

                currentActiveTicket = data;
                displayActiveResults(data);
                loadSavedComplaintsFromDB();
            } catch (err) {
                banner.classList.add('hidden');
                alert("Error connecting to backend API: " + err);
            }
        }

        function displayActiveResults(data) {
            const card = document.getElementById('prediction-card');
            card.classList.remove('hidden');

            document.getElementById('res-ticket-id').innerText = 'Ticket #' + data.ticket_id;
            document.getElementById('res-category').innerText = data.category;
            document.getElementById('res-domain').innerText = data.domain;
            document.getElementById('res-score').innerText = data.priority_score + '/100';

            // Route Badge Styling
            const rBadge = document.getElementById('res-route-badge');
            rBadge.innerText = data.route + ' ROUTE';
            if (data.route === 'Government') {
                rBadge.className = "px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-blue-100 text-blue-800 border border-blue-300";
            } else if (data.route === 'Innovation') {
                rBadge.className = "px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-purple-100 text-purple-800 border border-purple-300";
            } else {
                rBadge.className = "px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-pink-100 text-pink-800 border border-pink-300";
            }

            // ROUTE SCOPING UI RULES:
            // Government Route -> Show ONLY Govt Officer, Hide University Card
            // Innovation Route -> Show ONLY University, Hide Govt Officer Card
            // Hybrid Route -> Show BOTH Govt Officer AND University
            const govtWrapper = document.getElementById('govt-officer-wrapper');
            const heiWrapper = document.getElementById('hei-section-wrapper');

            if (data.route === 'Government') {
                govtWrapper.classList.remove('hidden');
                heiWrapper.classList.add('hidden');
                if (data.dept_assigned) {
                    document.getElementById('govt-dept').innerText = data.dept_assigned;
                    document.getElementById('govt-officer-name').innerText = data.officer_name;
                    document.getElementById('govt-escalation').innerText = data.escalation_officer;
                }
            } else if (data.route === 'Innovation') {
                govtWrapper.classList.add('hidden');
                heiWrapper.classList.remove('hidden');
            } else { // Hybrid
                govtWrapper.classList.remove('hidden');
                heiWrapper.classList.remove('hidden');
                if (data.dept_assigned) {
                    document.getElementById('govt-dept').innerText = data.dept_assigned;
                    document.getElementById('govt-officer-name').innerText = data.officer_name;
                    document.getElementById('govt-escalation').innerText = data.escalation_officer;
                }
            }

            // Single Best Matched University Details (for Innovation / Hybrid)
            const singleHeiCard = document.getElementById('single-hei-card');
            if (data.assigned_university && data.assigned_university !== 'N/A') {
                let rewardBadge = '';
                if (data.reward_granted && data.reward_granted !== 'NONE') {
                    rewardBadge = `<div class="p-2 bg-amber-50 rounded-xl border border-amber-300 text-amber-900 font-bold text-xs mt-2">
                        🏆 <strong>PROTOTYPE VERIFIED BY GOVT:</strong> ${data.reward_granted}
                    </div>`;
                }

                singleHeiCard.innerHTML = `
                    <div class="flex items-center justify-between border-b border-purple-100 pb-2">
                        <div>
                            <h4 class="text-sm font-bold text-slate-900">${data.assigned_university}</h4>
                            <p class="text-[11px] text-purple-700 font-semibold">Primary R&D Innovation Partner</p>
                        </div>
                        <span class="text-xs px-2.5 py-1 rounded-lg bg-purple-600 text-white font-black">
                            Top 1 Vector Match
                        </span>
                    </div>
                    <p class="text-xs text-emerald-700 font-bold bg-emerald-50 p-2 rounded border border-emerald-200 mt-2">
                        🎯 <strong>Assigned R&D Task:</strong> ${data.university_task}
                    </p>
                    ${rewardBadge}
                    <div id="hei-approval-status-text" class="text-[11px] font-bold text-amber-700 bg-amber-50 p-2 rounded border border-amber-200 mt-2">
                        ${data.status === 'PENDING_GOVT_VERIFICATION' ? '⏳ Status: Pending Govt Officer Proof Verification in Tab 2 before university starts R&D.' : '✔ Status: Verified by Govt Officer — University Prototyping Active!'}
                    </div>
                `;
            } else {
                singleHeiCard.innerHTML = '<p class="text-xs text-slate-500">Handled directly by Government Department Nodal Officer.</p>';
            }

            // Status Notice Banner
            const vNotice = document.getElementById('verification-notice-banner');
            const pBadge = document.getElementById('proof-status-badge');
            
            if (data.status === 'PENDING_GOVT_VERIFICATION') {
                vNotice.className = "p-4 rounded-2xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start space-x-3";
                vNotice.innerHTML = `
                    <span class="text-xl">⏳</span>
                    <div>
                        <p class="font-bold">Status: Pending Govt Nodal Officer Proof Verification</p>
                        <p class="text-amber-700 text-[11px] mt-0.5">
                            Grievance & photo proof saved in database! Govt Nodal Officer in <strong>Tab 2</strong> must inspect proof and verify before official allotment activates.
                        </p>
                    </div>
                `;
                pBadge.className = "px-2.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300";
                pBadge.innerText = "Pending Govt Proof Verification";
            } else {
                vNotice.className = "p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-start space-x-3";
                vNotice.innerHTML = `
                    <span class="text-xl">✔</span>
                    <div>
                        <p class="font-bold text-emerald-900">Status: Proof Verified & Action Approved by Govt Officer</p>
                        <p class="text-emerald-700 text-[11px] mt-0.5">
                            Verified by Executive Engineer Er. Alok Kumar Verma. Allotment active!
                        </p>
                    </div>
                `;
                pBadge.className = "px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300";
                pBadge.innerText = "✔ Verified & Action Live";
            }
        }

        async function loadSavedComplaintsFromDB() {
            try {
                const res = await fetch('/api/complaints');
                const complaints = await res.json();

                // Update KPI Counters
                document.getElementById('kpi-total-count').innerText = (4054 + complaints.length).toLocaleString();
                
                // Pending Govt Count
                const pendingGovt = complaints.filter(c => c.status === 'PENDING_GOVT_VERIFICATION');
                document.getElementById('badge-govt-pending').innerText = pendingGovt.length + ' Pending';

                // Allotted University Count
                const uniAllotted = complaints.filter(c => c.route === 'Innovation' || c.route === 'Hybrid');
                document.getElementById('badge-uni-count').innerText = uniAllotted.length + ' Allotted';

                // 1. Render Tab 1 Citizen History List
                const historyList = document.getElementById('grievance-history-list');
                historyList.innerHTML = '';
                complaints.forEach(c => {
                    const rColor = c.route === 'Government' ? 'blue' : (c.route === 'Innovation' ? 'purple' : 'pink');
                    const isPending = c.status === 'PENDING_GOVT_VERIFICATION';
                    const statusText = isPending ? '⏳ Pending Govt Verification' : (c.prototype_status === 'APPROVED_REWARD_ISSUED' ? '🏆 Prototype Verified & Grant Awarded' : '✔ Action Verified & Active');
                    const statusBg = isPending ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-emerald-100 text-emerald-800 border-emerald-200';

                    const assignedText = c.route === 'Government' ? `Officer: <strong>${c.officer_name}</strong>` : (c.route === 'Innovation' ? `University: <strong>${c.assigned_university}</strong>` : `Officer: <strong>${c.officer_name}</strong> | HEI: <strong>${c.assigned_university}</strong>`);

                    historyList.innerHTML += `
                        <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-between shadow-sm">
                            <div class="flex items-center space-x-3">
                                <div class="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-lg shadow-sm">
                                    ${c.route === 'Innovation' ? '🌾' : (c.domain.includes('Electricity') ? '⚡' : '🛣️')}
                                </div>
                                <div>
                                    <div class="flex items-center space-x-2">
                                        <span class="font-mono text-[10px] font-bold text-slate-500">#${c.ticket_id}</span>
                                        <span class="font-bold text-slate-900 text-xs">${c.complaint_text}</span>
                                        <span class="px-2 py-0.5 bg-${rColor}-100 text-${rColor}-800 text-[9px] font-bold rounded border border-${rColor}-200">${c.route.toUpperCase()} ROUTE</span>
                                    </div>
                                    <p class="text-[11px] text-slate-500 mt-0.5">${c.domain} | Category: <strong>${c.category}</strong></p>
                                    <p class="text-[10px] text-indigo-700 mt-0.5">Assigned Allotment: ${assignedText}</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <span class="px-2.5 py-1 rounded-lg text-[10px] font-bold border ${statusBg}">${statusText}</span>
                                <span class="text-[10px] text-slate-400 block mt-1">Proof: ${c.proof_filename}</span>
                            </div>
                        </div>
                    `;
                });

                // 2. Render Tab 2 Govt Verification Queue & Prototype Reward Desk
                const govtQueue = document.getElementById('govt-queue-container');
                govtQueue.innerHTML = '';

                const deptFilterVal = (document.getElementById('govt-dept-filter')?.value || 'ALL').toLowerCase();
                let displayGovtQueue = pendingGovt;
                if (deptFilterVal !== 'all') {
                    displayGovtQueue = pendingGovt.filter(c => 
                        (c.dept_assigned || '').toLowerCase().includes(deptFilterVal) || 
                        (c.domain || '').toLowerCase().includes(deptFilterVal)
                    );
                }

                if (displayGovtQueue.length === 0) {
                    govtQueue.innerHTML = `
                        <div class="p-6 bg-slate-50 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
                            🎉 No pending verification complaints for this department selection! (${pendingGovt.length} total pending in state feed).
                        </div>
                    `;
                } else {
                    displayGovtQueue.forEach(c => {
                        const targetAssigned = c.route === 'Government' ? `🏢 Dept: ${c.dept_assigned}<br>👤 Officer: ${c.officer_name}` : (c.route === 'Innovation' ? `🎓 HEI: ${c.assigned_university}` : `🏢 Dept: ${c.dept_assigned}<br>👤 Officer: ${c.officer_name}<br>🎓 HEI: ${c.assigned_university}`);
                        
                        govtQueue.innerHTML += `
                            <div class="p-5 bg-slate-50 border border-slate-200 rounded-2xl space-y-4 shadow-sm">
                                <div class="flex items-start justify-between">
                                    <div>
                                        <div class="flex items-center space-x-2 mb-1 flex-wrap gap-1">
                                            <span class="px-2.5 py-0.5 rounded bg-${c.route==='Government'?'blue':(c.route==='Innovation'?'purple':'pink')}-100 text-${c.route==='Government'?'blue':(c.route==='Innovation'?'purple':'pink')}-800 text-[10px] font-bold border border-slate-200">${c.route.toUpperCase()} ROUTE</span>
                                            <span class="px-2.5 py-0.5 rounded bg-indigo-100 text-indigo-800 text-[10px] font-bold border border-indigo-200">🏢 ${c.dept_assigned}</span>
                                            <span class="px-2.5 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-bold border border-rose-200">PRIORITY ${c.priority_score}/100</span>
                                            <span class="px-2.5 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-bold border border-amber-300">
                                                ⏳ Pending Officer Verification
                                            </span>
                                        </div>
                                        <h4 class="text-base font-bold text-slate-900">${c.complaint_text}</h4>
                                        <p class="text-xs text-slate-500">${c.domain} | Category: <strong>${c.category}</strong></p>
                                    </div>
                                    <span class="text-xs font-mono font-bold text-indigo-600">Ticket #${c.ticket_id}</span>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-white p-4 rounded-xl border border-slate-200 text-xs">
                                    <div>
                                        <span class="font-bold text-slate-500 block text-[10px] uppercase">Photo Proof File</span>
                                        <div class="mt-1 flex items-center space-x-2">
                                            <span class="text-2xl">📸</span>
                                            <div>
                                                <p class="font-bold text-slate-800">${c.proof_filename}</p>
                                                <p class="text-[10px] text-emerald-600 font-bold">📍 ${c.gps_location}</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div>
                                        <span class="font-bold text-slate-500 block text-[10px] uppercase">Department & Nodal Officer Allotment</span>
                                        <p class="font-bold text-slate-800 mt-1 leading-snug text-[11px]">${targetAssigned}</p>
                                    </div>
                                    <div>
                                        <span class="font-bold text-slate-500 block text-[10px] uppercase">SLA Target & Escalation</span>
                                        <p class="font-bold text-slate-900 mt-1">24 Hours SLA Target</p>
                                        <p class="text-[10px] text-rose-600 font-bold">Escalates to DC Ranchi: ${c.escalation_officer || 'Shri Rahul Sharma, IAS'}</p>
                                    </div>
                                </div>

                                <div class="flex items-center justify-between pt-2 border-t border-slate-200">
                                    <span class="text-xs text-slate-500">Verify proof authenticity to record Officer verification signature & dispatch to department:</span>
                                    <button onclick="officerApproveTicket('${c.ticket_id}')" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-sm transition">
                                        ✔ Verify Proof & Approve Ticket #${c.ticket_id}
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                }

                // Render SECTION 2: University R&D Prototype Audit & State Reward Desk
                const protoAuditContainer = document.getElementById('govt-prototype-audit-container');
                protoAuditContainer.innerHTML = '';

                const submittedPrototypes = complaints.filter(c => c.prototype_status === 'SUBMITTED_AWAITING_VERIFICATION' || c.prototype_status === 'APPROVED_REWARD_ISSUED');

                if (submittedPrototypes.length === 0) {
                    protoAuditContainer.innerHTML = `
                        <div class="p-6 bg-slate-50 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
                            No university R&D prototypes currently submitted for Govt audit. Universities submit prototypes in Tab 3.
                        </div>
                    `;
                } else {
                    submittedPrototypes.forEach(c => {
                        const isApproved = c.prototype_status === 'APPROVED_REWARD_ISSUED';
                        protoAuditContainer.innerHTML += `
                            <div class="p-5 bg-purple-50 border border-purple-200 rounded-2xl space-y-4 shadow-sm text-xs">
                                <div class="flex items-center justify-between border-b border-purple-200 pb-3">
                                    <div>
                                        <span class="px-2.5 py-0.5 rounded bg-purple-600 text-white font-bold text-[10px]">
                                            Ticket #${c.ticket_id} — University R&D Prototype Audit
                                        </span>
                                        <h4 class="text-sm font-bold text-slate-900 mt-1">${c.prototype_title}</h4>
                                        <p class="text-purple-800 font-semibold">Submitted by: <strong>${c.assigned_university}</strong></p>
                                    </div>
                                    <span class="px-3 py-1 rounded-full text-xs font-bold ${isApproved?'bg-emerald-100 text-emerald-800 border-emerald-300':'bg-amber-100 text-amber-800 border-amber-300'} border">
                                        ${isApproved?'🏆 Approved & ₹5,00,000 Reward Granted':'⏳ Pending Govt Audit Signature'}
                                    </span>
                                </div>

                                <div class="bg-white p-4 rounded-xl border border-purple-200 space-y-2">
                                    <p><strong>Original Grievance:</strong> "${c.complaint_text}"</p>
                                    <p><strong>Technical Description:</strong> ${c.prototype_description}</p>
                                    <p><strong>Demo Link:</strong> <a href="${c.prototype_demo_link}" target="_blank" class="text-indigo-600 font-bold hover:underline">${c.prototype_demo_link} ↗</a></p>
                                </div>

                                <div class="flex items-center justify-between pt-2">
                                    <span class="text-slate-600 font-bold">State R&D Excellence Award & ₹5,00,000 Grant Desk:</span>
                                    <button onclick="govtApprovePrototype('${c.ticket_id}')" ${isApproved?'disabled':''} class="px-5 py-2.5 ${isApproved?'bg-emerald-800 opacity-60 cursor-not-allowed':'bg-purple-700 hover:bg-purple-800 cursor-pointer'} text-white text-xs font-bold rounded-xl shadow-md transition">
                                        ${isApproved?'🏆 ₹5,00,000 Reward & Certificate Granted':'🏆 Approve Prototype & Issue ₹5,00,000 Reward'}
                                    </button>
                                </div>
                            </div>
                        `;
                    });
                }

                // 3. Render Tab 3 University Portal (ACCEPT / DECLINE & PROTOTYPE SUBMISSION)
                const uniTasksContainer = document.getElementById('university-allotted-tasks-container');
                uniTasksContainer.innerHTML = '';
                
                const innComplaints = complaints.filter(c => c.route === 'Innovation' || c.route === 'Hybrid');
                
                if (innComplaints.length === 0) {
                    uniTasksContainer.innerHTML = `
                        <div class="p-6 bg-slate-50 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
                            No active university innovation tasks in database yet. Submit an innovation complaint in Tab 1!
                        </div>
                    `;
                } else {
                    innComplaints.forEach(c => {
                        const isGovtVer = c.status !== 'PENDING_GOVT_VERIFICATION';
                        const isAccepted = c.university_status === 'ACCEPTED_IN_PROGRESS';
                        const isDeclined = c.university_status === 'DECLINED_REROUTED';
                        const isProtoSubmitted = c.prototype_status === 'SUBMITTED_AWAITING_VERIFICATION' || c.prototype_status === 'APPROVED_REWARD_ISSUED';
                        const isRewardGranted = c.prototype_status === 'APPROVED_REWARD_ISSUED';

                        let statusBadgeHtml = '';
                        if (!isGovtVer) {
                            statusBadgeHtml = '<span class="px-2 py-0.5 rounded bg-amber-500/30 text-amber-200 border border-amber-400/30 text-xs font-bold">⏳ Pending Govt Verification</span>';
                        } else if (isRewardGranted) {
                            statusBadgeHtml = '<span class="px-2 py-0.5 rounded bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 text-xs font-bold">🏆 Prototype Verified & ₹5,00,000 Reward Granted</span>';
                        } else if (isProtoSubmitted) {
                            statusBadgeHtml = '<span class="px-2 py-0.5 rounded bg-purple-500/30 text-purple-200 border border-purple-400/30 text-xs font-bold">⏳ Prototype Submitted ➔ Awaiting Govt Audit</span>';
                        } else if (isAccepted) {
                            statusBadgeHtml = '<span class="px-2 py-0.5 rounded bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 text-xs font-bold">✔ Accepted — R&D Active</span>';
                        } else if (isDeclined) {
                            statusBadgeHtml = '<span class="px-2 py-0.5 rounded bg-rose-500/30 text-rose-200 border border-rose-400/30 text-xs font-bold">⚠️ Primary Declined — Auto Re-routed</span>';
                        } else {
                            statusBadgeHtml = '<span class="px-2 py-0.5 rounded bg-purple-500/30 text-purple-200 border border-purple-400/30 text-xs font-bold">🔔 Allotted — Awaiting Decision</span>';
                        }

                        uniTasksContainer.innerHTML += `
                            <div class="p-6 bg-gradient-to-r from-purple-900 to-indigo-900 text-white rounded-3xl shadow-md space-y-4">
                                <div class="flex items-center justify-between">
                                    <span class="px-3 py-1 rounded-full bg-purple-400/20 text-purple-200 border border-purple-400/30 text-xs font-bold">
                                        Ticket #${c.ticket_id} — Assigned University R&D Task
                                    </span>
                                    <span class="text-xs font-mono text-purple-300">Assigned HEI: <strong>${c.assigned_university}</strong></span>
                                </div>
                                <div>
                                    <h4 class="text-lg font-bold">${c.assigned_university}</h4>
                                    <p class="text-xs text-purple-200 mt-1">${c.domain} | Category: ${c.category}</p>
                                </div>

                                <div class="p-4 bg-white/10 rounded-2xl border border-white/20 text-xs space-y-3">
                                    <div class="flex items-center justify-between">
                                        <span class="font-bold text-amber-300 text-sm">Allotted Complaint: "${c.complaint_text}"</span>
                                        ${statusBadgeHtml}
                                    </div>
                                    <p class="text-purple-200 bg-black/20 p-2.5 rounded-xl border border-white/10">
                                        🎯 <strong>Assigned R&D Task:</strong> ${c.university_task}
                                    </p>

                                    <!-- UNIVERSITY ACCEPT / DECLINE DECISION -->
                                    <div class="pt-2 flex items-center justify-between border-t border-white/10">
                                        <span class="text-[11px] text-purple-200">University Department Decision:</span>
                                        <div class="flex space-x-2">
                                            <button onclick="handleUniversityDecision('${c.ticket_id}', 'accept')" ${!isGovtVer || isAccepted ? 'disabled' : ''} class="px-3.5 py-1.5 ${!isGovtVer || isAccepted ? 'bg-emerald-800 opacity-50 cursor-not-allowed' : 'bg-emerald-600 hover:bg-emerald-500 cursor-pointer'} text-white text-xs font-bold rounded-xl transition">
                                                ✔ ${isAccepted ? 'Accepted' : 'Accept Allotment'}
                                            </button>
                                            <button onclick="handleUniversityDecision('${c.ticket_id}', 'decline')" ${!isGovtVer || isAccepted ? 'disabled' : ''} class="px-3.5 py-1.5 ${!isGovtVer || isAccepted ? 'bg-rose-900 opacity-40 cursor-not-allowed' : 'bg-rose-600 hover:bg-rose-500 cursor-pointer'} text-white text-xs font-bold rounded-xl transition">
                                                ✖ Decline & Re-route
                                            </button>
                                        </div>
                                    </div>

                                    <!-- PROTOTYPE SUBMISSION FORM (UNLOCKED AFTER ACCEPTING) -->
                                    ${isAccepted ? `
                                    <div class="mt-3 p-3.5 bg-black/30 rounded-2xl border border-white/20 space-y-2">
                                        <span class="font-bold text-amber-300 text-xs block">📤 Submit Working Prototype for Govt Audit & State Reward Grant</span>
                                        <input type="text" id="proto-title-${c.ticket_id}" value="IoT Smart NPK & Soil Moisture Meter Sensor Node v1.0" placeholder="Prototype Title" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-white placeholder-purple-300">
                                        <input type="text" id="proto-link-${c.ticket_id}" value="https://bauranchi.ac.in/prototypes/soil-sensor-v1" placeholder="Working Demo / Video Link" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-white placeholder-purple-300">
                                        <textarea id="proto-desc-${c.ticket_id}" rows="2" placeholder="Technical Description & Field Test Data" class="w-full bg-white/10 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-white placeholder-purple-300">Portable solar-powered NPK sensor node built with ESP32 micro-controller and Bluetooth mobile app calibration for Jharkhand small farmers.</textarea>
                                        <button onclick="submitPrototypeProofForm('${c.ticket_id}')" class="w-full py-2 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-xl shadow-md transition">
                                            🚀 Send Prototype to Govt Nodal Officer for ₹5,00,000 Reward Approval
                                        </button>
                                    </div>
                                    ` : ''}
                                </div>
                            </div>
                        `;
                    });
                }

            } catch (err) {
                console.error("Error loading complaints from DB:", err);
            }
        }

        async function officerApproveTicket(ticketId) {
            try {
                const res = await fetch('/api/complaint/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticket_id: ticketId })
                });

                const data = await res.json();
                if (data.status === 'ok') {
                    alert(`✔ Verification Complete for Ticket #${ticketId}! Govt Officer signature recorded. User Portal & University Portal updated!`);
                    loadSavedComplaintsFromDB();
                    if (currentActiveTicket && currentActiveTicket.ticket_id === ticketId) {
                        currentActiveTicket.status = 'GOVT_VERIFIED';
                        displayActiveResults(currentActiveTicket);
                    }
                }
            } catch (err) {
                alert("Error approving ticket: " + err);
            }
        }

        async function handleUniversityDecision(ticketId, action) {
            try {
                const res = await fetch('/api/complaint/university-decision', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticket_id: ticketId, action: action })
                });

                const data = await res.json();
                if (data.status === 'ok') {
                    alert(data.message);
                    loadSavedComplaintsFromDB();
                } else {
                    alert("Error: " + data.error);
                }
            } catch (err) {
                alert("Error executing university decision: " + err);
            }
        }

        async function submitPrototypeProofForm(ticketId) {
            const title = document.getElementById(`proto-title-${ticketId}`).value;
            const link = document.getElementById(`proto-link-${ticketId}`).value;
            const desc = document.getElementById(`proto-desc-${ticketId}`).value;

            if (!title || !link || !desc) {
                alert("Please fill in all prototype fields!");
                return;
            }

            try {
                const res = await fetch('/api/complaint/submit-prototype', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ticket_id: ticketId,
                        prototype_title: title,
                        prototype_demo_link: link,
                        prototype_description: desc
                    })
                });

                const data = await res.json();
                if (data.status === 'ok') {
                    alert(`🚀 Prototype "${title}" submitted to Govt Nodal Officer for Audit & ₹5,00,000 Reward Approval!`);
                    loadSavedComplaintsFromDB();
                } else {
                    alert("Error: " + data.error);
                }
            } catch (err) {
                alert("Error submitting prototype: " + err);
            }
        }

        async function govtApprovePrototype(ticketId) {
            try {
                const res = await fetch('/api/complaint/verify-prototype', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticket_id: ticketId })
                });

                const data = await res.json();
                if (data.status === 'ok') {
                    alert(data.message);
                    loadSavedComplaintsFromDB();
                } else {
                    alert("Error: " + data.error);
                }
            } catch (err) {
                alert("Error approving prototype: " + err);
            }
        }

        function verifyResolution(isAccepted) {
            const pBadge = document.getElementById('proof-status-badge');
            if (isAccepted) {
                pBadge.className = "px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300";
                pBadge.innerText = "✔ Resolved & Confirmed by Citizen";
                alert("Thank you! Resolution confirmed. Ticket officially closed with citizen verification signature.");
            } else {
                pBadge.className = "px-2.5 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-300";
                pBadge.innerText = "✖ Rejected — Auto-Escalated to Tier 3 DC Office";
                alert("Resolution rejected by citizen. Case re-opened and auto-escalated to District Magistrate for SLA audit.");
            }
        }

        async function searchTicketProgress() {
            const q = document.getElementById('ticket-search-input').value.trim();
            if (!q) return;

            try {
                const res = await fetch('/api/complaints');
                const list = await res.json();
                const found = list.find(c => c.ticket_id.toLowerCase() === q.toLowerCase());

                if (found) {
                    document.getElementById('search-ticket-title').innerText = 'Ticket ID: #' + found.ticket_id;
                    document.getElementById('search-problem-text').innerText = 'Problem: "' + found.complaint_text + '"';
                    document.getElementById('search-route-info').innerText = 'Route: ' + found.route + ' | Domain: ' + found.domain;

                    const isVer = found.status !== 'PENDING_GOVT_VERIFICATION';
                    
                    document.getElementById('search-current-status').innerText = isVer ? '✔ Govt Verified & Active' : '⏳ Pending Govt Verification';
                    document.getElementById('search-current-status').className = isVer ? 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300' : 'px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300';

                    document.getElementById('timeline-node-3').className = isVer ? 'w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-[10px]' : 'w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center font-bold text-[10px]';
                    document.getElementById('timeline-text-3').innerText = isVer ? 'Govt Officer Proof Verified & Order Approved' : 'Govt Officer Proof Verification Pending';
                    document.getElementById('timeline-subtext-3').innerText = isVer ? 'Approved by Er. Alok Kumar Verma' : 'Awaiting Officer Signature in Tab 2';

                    document.getElementById('timeline-node-4').className = isVer ? 'w-6 h-6 rounded-full bg-purple-500 text-white flex items-center justify-center font-bold text-[10px]' : 'w-6 h-6 rounded-full bg-slate-300 text-slate-600 flex items-center justify-center font-bold text-[10px]';
                    document.getElementById('timeline-text-4').className = isVer ? 'font-bold text-slate-900' : 'font-bold text-slate-400';
                    
                    if (found.route === 'Innovation') {
                        document.getElementById('timeline-text-4').innerText = 'Allotted University: ' + found.assigned_university;
                    } else if (found.route === 'Government') {
                        document.getElementById('timeline-text-4').innerText = 'Allotted Nodal Officer: ' + found.officer_name;
                    } else {
                        document.getElementById('timeline-text-4').innerText = 'Hybrid: ' + found.officer_name + ' & ' + found.assigned_university;
                    }
                    document.getElementById('timeline-subtext-4').innerText = isVer ? 'Task Active' : 'Pending Govt Verification';

                    alert(`✔ Found Ticket #${found.ticket_id} in System Database!`);
                } else {
                    alert(`Ticket ID '${q}' not found in System Database.`);
                }
            } catch (err) {
                alert("Search error: " + err);
            }
        }

        async function loadInstitutions() {
            const grid = document.getElementById('institution-cards-grid');
            grid.innerHTML = '<p class="text-xs text-slate-500 col-span-2">Loading institution database...</p>';
            try {
                const res = await fetch('/api/institutions');
                const data = await res.json();
                grid.innerHTML = '';
                data.forEach(inst => {
                    grid.innerHTML += `
                        <div class="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-sm">
                            <div class="flex items-center justify-between">
                                <h4 class="text-sm font-bold text-slate-900">${inst.institution_name}</h4>
                                <span class="text-[10px] px-2 py-0.5 rounded bg-purple-50 text-purple-700 font-bold border border-purple-200">${inst.institution_type}</span>
                            </div>
                            <p class="text-xs text-slate-700"><strong>Research Focus:</strong> ${inst.research_area}</p>
                            <p class="text-xs text-slate-500"><strong>Potential Role:</strong> ${inst.potential_contribution}</p>
                            <a href="${inst.verification_source}" target="_blank" class="inline-block text-xs text-indigo-600 hover:underline font-bold">Official Verification Link ↗</a>
                        </div>
                    `;
                });
            } catch (err) {
                grid.innerHTML = '<p class="text-xs text-rose-600 col-span-2">Failed to load institutions.</p>';
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            loadSavedComplaintsFromDB();
            loadInstitutions();
        });
    </script>
</body>
</html>
"""

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/predict", methods=["POST", "OPTIONS"])
def api_predict():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.get_json() or {}
    text = data.get("complaint_text", "")
    if not text:
        return jsonify({"error": "No complaint text provided"}), 400
    
    full_prediction_package = predict_complaint(text)
    return jsonify(full_prediction_package)

@app.route("/api/complaint/submit", methods=["POST", "OPTIONS"])
def api_complaint_submit():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.get_json() or {}
    text = data.get("complaint_text", "").strip()
    proof = data.get("proof_filename", "").strip()
    gps = data.get("gps_location", "Ranchi Ward 4, Jharkhand")

    if not text:
        return jsonify({"error": "Complaint statement is required"}), 400
    if not proof:
        return jsonify({"error": "Photo/Video proof is MANDATORY to submit a grievance!"}), 400

    pred_package = predict_complaint(text)
    results = pred_package["results"]
    gov_officer = pred_package.get("government_officer") or {}
    priority_metrics = pred_package.get("priority_metrics", {})
    matched_institutions = pred_package.get("matched_institutions", [])
    backup_uni = pred_package.get("backup_university", "BIT Mesra, Ranchi")

    # Scoped Route Values
    dept_assigned = gov_officer.get("department_assigned", "Department of Urban / Rural Development") if gov_officer else "N/A"
    officer_name = gov_officer.get("primary_officer_name", "Er. Alok Kumar Verma") if gov_officer else "N/A"
    escalation_officer = gov_officer.get("escalation_officer_name", "Shri Rahul Sharma, IAS (DC Ranchi)") if gov_officer else "N/A"

    assigned_uni = matched_institutions[0]["institution_name"] if matched_institutions else "N/A"
    uni_task = matched_institutions[0]["potential_contribution"] if matched_institutions else "N/A"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]
    ticket_id = f"SS-{1001 + count}"

    cursor.execute("""
    INSERT INTO complaints (
        ticket_id, complaint_text, proof_filename, gps_location,
        domain, category, route, severity, priority_score, status,
        dept_assigned, officer_name, escalation_officer,
        assigned_university, backup_university, university_task, university_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id, text, proof, gps,
        results["domain"], results["category"], results["route"], results["severity"],
        priority_metrics.get("priority_score", 85), "PENDING_GOVT_VERIFICATION",
        dept_assigned, officer_name, escalation_officer,
        assigned_uni, backup_uni, uni_task, "PENDING_DECISION"
    ))
    conn.commit()
    conn.close()

    response_payload = {
        "ticket_id": ticket_id,
        "complaint_text": text,
        "proof_filename": proof,
        "gps_location": gps,
        "domain": results["domain"],
        "category": results["category"],
        "route": results["route"],
        "severity": results["severity"],
        "priority_score": priority_metrics.get("priority_score", 85),
        "status": "PENDING_GOVT_VERIFICATION",
        "dept_assigned": dept_assigned,
        "officer_name": officer_name,
        "escalation_officer": escalation_officer,
        "assigned_university": assigned_uni,
        "backup_university": backup_uni,
        "university_task": uni_task,
        "university_status": "PENDING_DECISION",
        "full_pred": pred_package
    }
    return jsonify(response_payload)

@app.route("/api/complaints", methods=["GET"])
def api_get_complaints():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    result = [dict(row) for row in rows]
    return jsonify(result)

@app.route("/api/complaint/verify", methods=["POST", "OPTIONS"])
def api_complaint_verify():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.get_json() or {}
    ticket_id = data.get("ticket_id", "")

    if not ticket_id:
        return jsonify({"error": "Ticket ID required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status = 'GOVT_VERIFIED' WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "message": f"Ticket {ticket_id} verified and approved by Govt Officer"})

@app.route("/api/complaint/university-decision", methods=["POST", "OPTIONS"])
def api_complaint_university_decision():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.get_json() or {}
    ticket_id = data.get("ticket_id", "")
    action = data.get("action", "")

    if not ticket_id or not action:
        return jsonify({"error": "Ticket ID and action required"}), 400

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Ticket not found"}), 404

    complaint = dict(row)

    if action == "accept":
        cursor.execute("UPDATE complaints SET university_status = 'ACCEPTED_IN_PROGRESS' WHERE ticket_id = ?", (ticket_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok", "message": f"✔ Allotment ACCEPTED by {complaint['assigned_university']} for Ticket #{ticket_id}! Prototyping active."})

    elif action == "decline":
        backup_uni = complaint.get("backup_university") or "BIT Mesra, Ranchi"
        if backup_uni == "N/A" or backup_uni == complaint["assigned_university"]:
            backup_uni = "BIT Mesra, Ranchi"

        cursor.execute("""
        UPDATE complaints SET 
            assigned_university = ?, 
            university_status = 'DECLINED_REROUTED' 
        WHERE ticket_id = ?
        """, (backup_uni, ticket_id))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "ok", 
            "message": f"⚠️ Ticket #{ticket_id} DECLINED by primary university. AUTOMATICALLY RE-ROUTED TO BACKUP UNIVERSITY: {backup_uni}!"
        })

@app.route("/api/complaint/submit-prototype", methods=["POST", "OPTIONS"])
def api_complaint_submit_prototype():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.get_json() or {}
    ticket_id = data.get("ticket_id", "")
    title = data.get("prototype_title", "")
    link = data.get("prototype_demo_link", "")
    desc = data.get("prototype_description", "")

    if not ticket_id or not title:
        return jsonify({"error": "Ticket ID and prototype title required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE complaints SET 
        prototype_title = ?,
        prototype_demo_link = ?,
        prototype_description = ?,
        prototype_status = 'SUBMITTED_AWAITING_VERIFICATION'
    WHERE ticket_id = ?
    """, (title, link, desc, ticket_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "message": f"🚀 Prototype '{title}' submitted to Govt Nodal Officer for Audit & Reward Approval!"})

@app.route("/api/complaint/verify-prototype", methods=["POST", "OPTIONS"])
def api_complaint_verify_prototype():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    data = request.get_json() or {}
    ticket_id = data.get("ticket_id", "")

    if not ticket_id:
        return jsonify({"error": "Ticket ID required"}), 400

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Ticket not found"}), 404

    complaint = dict(row)
    reward_title = "State R&D Grant ₹5,00,000 + SIH 2026 Excellence Award Certificate"

    cursor.execute("""
    UPDATE complaints SET 
        prototype_status = 'APPROVED_REWARD_ISSUED',
        reward_granted = ?
    WHERE ticket_id = ?
    """, (reward_title, ticket_id))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok",
        "message": f"🏆 PROTOTYPE VERIFIED & APPROVED! Granted ₹5,00,000 State R&D Grant & Certificate to {complaint['assigned_university']} for Ticket #{ticket_id}!"
    })

@app.route("/api/institutions", methods=["GET"])
def api_institutions():
    inst_df = load_institution_db()
    if inst_df.empty:
        return jsonify([])
    return jsonify(inst_df.to_dict(orient="records"))

if __name__ == "__main__":
    print("[*] Starting Samadhan Setu Master Flask Web Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
