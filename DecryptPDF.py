import os
import PyPDF2

def decrypt_pdf_files(directory):
    """
    Scans a directory for PDF files, decrypts them, and saves the decrypted files.

    Args:
        directory (str): The path to the directory containing the PDF files.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".pdf") or filename.endswith(".PDF")and "_decrypted" not in filename:
            # Extract the password from the filename
            parts = filename.split("_")
            if len(parts) > 1:
                password = parts[-1].split(".")[0]
                print(password)
                #password = "BCPPA8832C"
                input_file = os.path.join(directory, filename)
                output_file = os.path.join(directory, f"{'_'.join(parts[:-1])}_decrypted.pdf")

                try:
                    # Open the PDF file in read-binary mode
                    with open(input_file, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)

                        # Check if the PDF is encrypted
                        if pdf_reader.is_encrypted:
                            # Decrypt the PDF using the provided password
                            if pdf_reader.decrypt(password) == 2:
                                print(f"Password is correct for {filename}. Decrypting PDF...")

                                # Create a PDF writer object
                                pdf_writer = PyPDF2.PdfWriter()

                                # Add all pages from the input PDF to the writer
                                for page in pdf_reader.pages:
                                    pdf_writer.add_page(page)

                                # Write the decrypted PDF to the output file
                                with open(output_file, 'wb') as output:
                                    pdf_writer.write(output)

                                print(f"PDF decrypted and saved to {output_file}")

                                # Delete the original file
                                os.remove(input_file)
                                print(f"Original file {filename} deleted.")
                            else:
                                print(f"Incorrect password for {filename}. Skipping...")
                        else:
                            print(f"{filename} is not encrypted. Skipping...")
                except Exception as e:
                    print(f"An error occurred while processing {filename}: {e}")

# Example usage:
directory = "/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/NAS/1_Document/0DecryptionFolder"
decrypt_pdf_files(directory)
