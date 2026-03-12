import sys
import pipeline_config # Our global brain

# Standardized Imports
import March10_stage0_Sanitization as stage0
import March10_stage2_3_OCR as stage23
import Stage3_5_Metadata as stage35
import March10_stage4_Extraction as stage4
import March10_stage5_Audit as stage5
import March10_stage6_comparemodels as stage6

def run_menu():
    pipeline_config.ensure_dirs()
    
    while True:
        print("\n" + "="*55)
        print(f"🧬 MASTER AI RESEARCH ENGINE")
        print(f"   Topic: {pipeline_config.CURRENT_TOPIC.upper()} | Model: {pipeline_config.CURRENT_MODEL}")
        print("="*55)
        print("[0] STAGE 0: Foundation (Sanitize & Backup)")
        print("[1] STAGE 2-3: Librarian (Audit Gaps & OCR Fill)")
        print("[2] STAGE 3.5: Metadata (Aggregate Word Counts)")
        print("[3] STAGE 4: Extraction (Categorize Quotes)")
        print("[4] STAGE 5: Auditor (Analysis & Density)")
        print("[5] STAGE 6: Compare Models (Dashboard)")
        print("[A] FULL RUN (Execute Stages 0-6 in sequence)")
        print("[q] Quit")
        print("="*55)

        choice = input("\nAction: ").strip().lower()

        if choice == '0':
            stage0.run_stage_0_sanitization()
        elif choice == '1':
            stage23.run_librarian_pipeline()
        elif choice == '2':
            stage35.run_stage_3_5_aggregator()
        elif choice == '3':
            stage4.run_model_specific_stage_4()
        elif choice == '4':
            stage5.run_comparative_audit()
        elif choice == '5':
            stage6.run_stage_6_comparison()
        elif choice == 'a':
            print("\n🚀 STARTING FULL AUTOMATED RUN...")
            stage0.run_stage_0_sanitization()
            stage23.run_librarian_pipeline()
            stage35.run_stage_3_5_aggregator()
            stage4.run_model_specific_stage_4()
            stage5.run_comparative_audit()
            stage6.run_stage_6_comparison()
            print("\n✨ FULL PIPELINE SEQUENCE COMPLETE.")
        elif choice == 'q':
            print("👋 Closing lab. Goodbye!")
            break

if __name__ == "__main__":
    run_menu()