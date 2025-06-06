import sys
import os

print("--- Python Executable ---")
print(sys.executable)
print("-" * 30)

print("--- sys.path (Search Paths for Modules) ---")
for pth in sys.path:
    print(pth)
print("--- end of sys.path ---")
print("-" * 30)

# Έλεγχος της μεταβλητής περιβάλλοντος PYTHONPATH
print("--- PYTHONPATH Environment Variable ---")
pythonpath_env = os.getenv("PYTHONPATH")
if pythonpath_env:
    print(f"Η μεταβλητή PYTHONPATH είναι ΟΡΙΣΜΕΝΗ σε: {pythonpath_env}")
else:
    print("Η μεταβλητή PYTHONPATH ΔΕΝ είναι ορισμένη.")
print("-" * 30)

print("--- Importing and Checking fitz (PyMuPDF) ---")
try:
    import fitz
    print(f"INFO: Η εισαγωγή της βιβλιοθήκης fitz έγινε επιτυχώς.")

    # Έκδοση της βιβλιοθήκης fitz
    print(f"fitz.__version__: {getattr(fitz, '__version__', 'N/A')}")

    # Διαδρομή αρχείου της βιβλιοθήκης fitz (από πού φορτώθηκε)
    print(f"fitz.__file__: {getattr(fitz, '__file__', 'N/A')}") # ΚΡΙΣΙΜΟ

    # Έλεγχος για την ύπαρξη του TEXTFLAGS_FONTS απευθείας στο fitz module
    has_textflags_on_fitz = hasattr(fitz, 'TEXTFLAGS_FONTS')
    print(f"hasattr(fitz, 'TEXTFLAGS_FONTS'): {has_textflags_on_fitz}") # ΚΡΙΣΙΜΟ

    if has_textflags_on_fitz:
        try:
            print(f"Value of fitz.TEXTFLAGS_FONTS: {fitz.TEXTFLAGS_FONTS}")
        except Exception as e_val:
            print(f"Could not get value of fitz.TEXTFLAGS_FONTS: {e_val}")
    else:
        print("Το χαρακτηριστικό 'TEXTFLAGS_FONTS' ΔΕΝ βρέθηκε απευθείας στο module 'fitz'.")

    # Έλεγχος στο fitz.mupdf (παλαιότερες εκδόσεις ή εσωτερική δομή)
    print("\n--- Checking fitz.mupdf (if it exists and has the flag) ---")
    if hasattr(fitz, 'mupdf'):
        print("INFO: Το υπο-module 'fitz.mupdf' υπάρχει.")
        has_textflags_on_mupdf = hasattr(fitz.mupdf, 'TEXTFLAGS_FONTS')
        print(f"hasattr(fitz.mupdf, 'TEXTFLAGS_FONTS'): {has_textflags_on_mupdf}")
        if has_textflags_on_mupdf:
            try:
                print(f"Value of fitz.mupdf.TEXTFLAGS_FONTS: {fitz.mupdf.TEXTFLAGS_FONTS}")
            except Exception as e_mval:
                print(f"Could not get value of fitz.mupdf.TEXTFLAGS_FONTS: {e_mval}")
        else:
            print("Το χαρακτηριστικό 'TEXTFLAGS_FONTS' ΔΕΝ βρέθηκε στο 'fitz.mupdf'.")
    else:
        print("INFO: Το υπο-module 'fitz.mupdf' ΔΕΝ υπάρχει (αναμενόμενο για νεότερες εκδόσεις PyMuPDF >= 1.19.0).")
        print("INFO: Για σύγχρονες εκδόσεις PyMuPDF, το TEXTFLAGS_FONTS θα πρέπει να είναι στο 'fitz' module απευθείας.")

except ImportError as e_import:
    print(f"ΣΟΒΑΡΟ ΣΦΑΛΜΑ: Δεν ήταν δυνατή η εισαγωγή της βιβλιοθήκης fitz (PyMuPDF). {e_import}")
    print("Παρακαλώ βεβαιωθείτε ότι το PyMuPDF είναι σωστά εγκατεστημένο στο εικονικό σας περιβάλλον.")
    print(f"Έγινε προσπάθεια φόρτωσης από τον Python interpreter: {sys.executable}")
except Exception as e_general:
    print(f"Προέκυψε ένα μη αναμενόμενο σφάλμα: {e_general}")

print("-" * 30)
print("--- Τέλος Διαγνωστικού Script ---")