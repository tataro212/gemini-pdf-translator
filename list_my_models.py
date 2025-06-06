import google.generativeai as genai
import os
from dotenv import load_dotenv

# Φόρτωση του .env αρχείου για το API key
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

if not API_KEY:
    print("Σφάλμα: Το GEMINI_API_KEY δεν βρέθηκε στο .env αρχείο σας.")
    print("Παρακαλώ βεβαιωθείτε ότι το αρχείο .env υπάρχει στον ίδιο φάκελο με αυτό το script")
    print("και περιέχει τη γραμμή: GEMINI_API_KEY=ΤΟ_API_KEY_ΣΑΣ")
else:
    try:
        genai.configure(api_key=API_KEY)
        print("Επιτυχής ρύθμιση API key.")
        print("\nΔιαθέσιμα μοντέλα που υποστηρίζουν 'generateContent':")

        count = 0
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"\nΌνομα για API (m.name): {m.name}")
                print(f"  Εμφανιζόμενο Όνομα (Display Name): {m.display_name}")
                print(f"  Περιγραφή: {m.description[:100]}...") # Εμφάνιση των πρώτων 100 χαρακτήρων
                print(f"  Όριο Tokens Εισόδου: {m.input_token_limit}")
                print(f"  Όριο Tokens Εξόδου: {m.output_token_limit}")
                print(f"  Υποστηριζόμενες Μέθοδοι: {m.supported_generation_methods}")
                count += 1

        if count == 0:
            print("\nΔεν βρέθηκαν διαθέσιμα μοντέλα που να υποστηρίζουν 'generateContent' με αυτό το API key μέσω αυτού του SDK.")
            print("Πιθανές αιτίες:")
            print("- Το API key δεν έχει δικαιώματα για τα κατάλληλα μοντέλα.")
            print("- Το project στο Google Cloud δεν έχει ενεργοποιημένες τις απαραίτητες υπηρεσίες (π.χ., Generative Language API ή Vertex AI API).")
            print("- Βρίσκεστε σε περιοχή (region) όπου τα επιθυμητά μοντέλα δεν είναι διαθέσιμα με αυτό το API key.")
        else:
            print(f"\nΣυνολικά βρέθηκαν {count} κατάλληλα μοντέλα.")

        print("\nΣΗΜΑΝΤΙΚΟ: Για το κυρίως script σας (ultimate_pdf_translator.py),")
        print("χρησιμοποιήστε την τιμή από το πεδίο 'Όνομα για API (m.name)' (π.χ., 'models/gemini-1.5-pro-latest')")
        print("για τη μεταβλητή MODEL_NAME.")

    except Exception as e:
        print(f"Προέκυψε σφάλμα κατά την προσπάθεια λίστας των μοντέλων: {e}")
        print("Πιθανές αιτίες:")
        print("- Το API key είναι όντως άκυρο (ακόμα κι αν δεν έβγαλε σφάλμα το configure).")
        print("- Δεν υπάρχει σύνδεση στο διαδίκτυο.")
        print("- Κάποιο πρόβλημα με τις υπηρεσίες της Google.")