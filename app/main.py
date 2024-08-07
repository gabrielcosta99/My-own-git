import hashlib
import sys
import os
import zlib


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    #
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")

    ######## Second Exercise ############
    elif command == "cat-file": # cats a file from the "objects" folder inside of ".git"
        if sys.argv[2] == "-p":
            file = sys.argv[3]
            with open(f".git/objects/{file[:2]}/{file[2:]}","rb") as f:     # the first two chars are the name of the folder, the rest is the name of the file
                content = zlib.decompress(f.read())         # decompress the content file
                # a blob format after zlib decompression is "blob <size>\0<content>" (example: blob 11\0hello world)
                header, content = content.split(b"\0")  # so we have to split by the "\0"            
                print(content.decode("utf-8"),end="")

         
    ######## Third Exercise ############
    elif command == "hash-object":  # Compute the SHA-1 hash of the file and write it to .git/objects
        if sys.argv[2] == "-w":
            file = sys.argv[3]  # Get the file name from the command line arguments
            f = open(file, "rb")  # Open the file in binary read mode
            content = f.read()  # Read the entire content of the file

            # Create the header for the blob object, which includes the type 'blob' and the length of the content
            header = f"blob {len(content)}\x00"
            store = header.encode("ascii") + content  # Combine the header and the content
            
            # Compute the SHA-1 hash of the header+content
            sha = hashlib.sha1(store).hexdigest()

            # Compress the header+content using zlib
            comp = zlib.compress(store)

            # Create the necessary directories in .git/objects based on the hash
            if not os.path.isdir(f".git/objects/{sha[:2]}"):
                os.mkdir(f".git/objects/{sha[:2]}")
            
            # If a file with the same hash already exists, remove it
            if os.path.exists(f".git/objects/{sha[:2]}/{sha[2:]}"):
                os.remove(f".git/objects/{sha[:2]}/{sha[2:]}")

            # Write the compressed data to the appropriate file in .git/objects
            with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f2: 
                f2.write(comp)

            print(sha)  # Print the hash to the console

            f.close()  # Close the original file

    ######## Fourth Exercise ############
    elif command=="ls-tree": 
        if sys.argv[2] == "--name-only":
            file = sys.argv[3]
            with open(f".git/objects/{file[:2]}/{file[2:]}","rb") as f:     # the first two chars are the name of the folder, the rest is the name of the file
                decompressed_data = zlib.decompress(f.read())         # decompress the content file
                _, data = decompressed_data.split(b"\0",maxsplit=1)  # remove the header

                while len(data)>0:
                    line,data = data.split(b"\0",maxsplit=1)    #line example: \x1f\x00\x9c\xac\xcd\xae\xc5\x8d\xe9U\x04P\x9a\xae/a\xf7s\xd4\xdf100644 test.txt
                    _,name = line.split()
                    print(name.decode())  
                    data = data[20:]                            #remove the sha characters 
    
        else:               # ls-tree
            file = sys.argv[2]
            with open(f".git/objects/{file[:2]}/{file[2:]}","rb") as f:     # the first two chars are the name of the folder, the rest is the name of the file
                decompressed_data = zlib.decompress(f.read())         # decompress the content file
                _, data = decompressed_data.split(b"\0",maxsplit=1)  # remove the header

                # Process the first line of the data
                line, data = data.split(b"\0", maxsplit=1)
                mode, name = line.split()
                while len(data)>0:
                    sha = data[:21] # the first 20 characters are 'sha encoded bytes'
                    file_type = "blob"
                    # if str(mode.decode()) == "100644" or str(mode.decode()) == "100755": 
                    #     file_type = "blob"
                    if str(mode.decode()) == "40000": 
                        mode = b"0"+mode
                        file_type = "tree"
                    elif str(mode.decode()) == "120000": 
                        file_type = "link"
                    print(f"{mode.decode()} {file_type} {hashlib.sha1(sha).hexdigest()} {name.decode()}")  
                    if len(data)> 20:
                        line,data = data[20:].split(b"\0",maxsplit=1)
                        mode, name = line.split()
                    else:
                        break
    
    
    elif "write-tree":
        file = os.getcwd()
        print(os.listdir(file))
    
                
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
