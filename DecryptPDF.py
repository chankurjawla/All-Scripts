import os
import PyPDF2

def decrypt_pdf_files(directory):
    for filename in os.listdir(directory):
        # lower() handles .pdf and .PDF in one go
        if filename.lower().endswith(".pdf") and "_decrypted" not in filename:
            
            # Use rsplit to split from the right, ensuring we only remove the extension
            # Then split by "_" to find the password
            name_part = filename.rsplit(".", 1)[0]
            parts = name_part.split("_")
            
            if len(parts) > 1:
                password = parts[-1]  # The last part after the last underscore
                input_file = os.path.join(directory, filename)
                
                # Reconstruct name without the password for the output
                clean_name = "_".join(parts[:-1])
                output_file = os.path.join(directory, f"{clean_name}_decrypted.pdf")

                try:
                    with open(input_file, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)

                        if pdf_reader.is_encrypted:
                            # 1 = User Password, 2 = Owner Password
                            decrypt_status = pdf_reader.decrypt(password)
                            
                            if decrypt_status in (1, 2):
                                print(f"Success: Decrypting {filename}...")
                                pdf_writer = PyPDF2.PdfWriter()

                                for page in pdf_reader.pages:
                                    pdf_writer.add_page(page)

                                with open(output_file, 'wb') as output:
                                    pdf_writer.write(output)

                                # Important: Close the file handle before deleting!
                                file.close() 
                                os.remove(input_file)
                                print(f"Done. Original removed.")
                            else:
                                print(f"Fail: Wrong password for {filename}.")
                        else:
                            print(f"Skip: {filename} is not encrypted.")
                except Exception as e:
                    print(f"Error on {filename}: {e}")

directory = "/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/NAS/1_Document/0DecryptionFolder"
decrypt_pdf_files(directory)