import sys
from pathlib import Path

# --- CORRECTED IMPORTS ---
try:
    # Stage 0: Pre-flight and Workspace Architect
    from March3_stage_0_folder_verification import run_stage_0_validation_and_organize
    # Stage 1: The Digitizer
    from March3_stage_1_digitizer import run_stage_1_digitizer
    
    # Stage 2-3: The Librarian (Audit & Smart Fill)
    from March3_stage2_3_master_runner import run_librarian_pipeline
    
    # Stage 4: Hierarchical Thematic Extraction
    from March4_stage4_extracttheme_awareofbefore import run_stage_4_nature_extraction
    
    # Stage 5: The Wise Auditor
    from March2_stage5_nature_auditor import run_stage_5_wise_audit
    
    # Stage 6: Performance Purifier
    from March2_stage6_performance_purifier import run_performance_summary
    
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    print("💡 Suggestion: Ensure all .py files are in the same folder as this main.py.")
    sys.exit(1)

def print_menu():
    print("\n" + "="*50)
    print("🧩 NATURE AI RESEARCH PIPELINE ORCHESTRATOR")
    print("="*50)
    print("[0] Stage 0: Pre-flight (Validate & Organize Workspace)")
    print("[1] Process A: The Librarian (Stages 1-3: Digitization)")
    print("[2] Process B: The Research (Stages 4-6: Extraction & Gold Standard)")
    print("[3] Full Pipeline: End-to-End (Stages 0-6)")
    print("[q] Quit")

def main():
    while True:
        print_menu()
        choice = input("\nSelect an action: ").strip().lower()

        if choice == '0':
            run_stage_0_validation_and_organize()

        elif choice == '1':
            print("\n📦 Starting Process A: Digitization...")
            run_stage_1_digitizer()
            run_librarian_pipeline() 
            print("\n✅ Process A Complete.")

        elif choice == '2':
            print("\n🌿 Starting Process B: Research & Purification...")
            # These steps now follow the [Book_Name_Timestamp]/[Stage_Version] logic
            run_stage_4_nature_extraction()
            run_stage_5_wise_audit()
            run_performance_summary()
            print("\n✅ Process B Complete.")

        elif choice == '3':
            print("\n🚀 Executing Full End-to-End Research Engine...")
            run_stage_0_validation_and_organize()
            run_stage_1_digitizer()
            run_librarian_pipeline()
            run_stage_4_nature_extraction()
            run_stage_5_wise_audit()
            run_performance_summary()
            print("\n✅ Full Execution Finished.")

        elif choice == 'q':
            print("👋 Session Closed.")
            break
        else:
            print("⚠️ Invalid entry.")

if __name__ == "__main__":
    main()