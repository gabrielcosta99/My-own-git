import hashlib
import sys
import os
import zlib
import stat

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
            sha = hash_file(file)
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
        print(get_tree_files("./"))
     
    # elif "write-tree":
    #     # print(write_tree("./"))
    #     cwd = os.getcwd()
    #     #print(os.listdir(file))
    #     tree_sequence = get_tree_files(sorted(os.listdir(cwd)))
    #     #print(tree_sequence,size)
    #     print(tree_sequence)
    #     header = f"tree {len(tree_sequence)}\0"
    #     store =  header.encode() + tree_sequence
    #     sha = hashlib.sha1(store).hexdigest()

    #     comp = zlib.compress(store)
    #     # Create the necessary directories in .git/objects based on the hash
    #     if not os.path.isdir(f".git/objects/{sha[:2]}"):
    #         os.mkdir(f".git/objects/{sha[:2]}")
        
    #     # If a file with the same hash already exists, remove it
    #     if os.path.exists(f".git/objects/{sha[:2]}/{sha[2:]}"):
    #         os.remove(f".git/objects/{sha[:2]}/{sha[2:]}")

    #     # Write the compressed data to the appropriate file in .git/objects
    #     with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f: 
    #         f.write(comp)
    #     print(sha)


    else:
        raise RuntimeError(f"Unknown command #{command}")


def get_tree_files(file):
    if os.path.isfile(file):
        return hash_file(file)
    
    #if we got here, we are handling a directory
    string = b""
    files = sorted(os.listdir(file),
        key=lambda x: x if os.path.isfile(os.path.join(file, x)) else f"{x}/",)
    #print(files)
    for f in files:
        if f == ".git":
            continue
        path = os.path.join(file, f)
        if os.path.isfile(path):
            file_stat = os.stat(path)
            is_executable = file_stat.st_mode & stat.S_IXUSR != 0
            mode = "100755" if is_executable else "100644"
            string+=f"{mode} {f}\0".encode()
        else:
            mode = "40000"
            string+=f"{mode} {f}\0".encode()

        sha = int.to_bytes(int(get_tree_files(path),base=16),length=20,byteorder="big")

        string+=sha
    string = f"tree {len(string)}\0".encode()+string
    sha = hashlib.sha1(string).hexdigest()


    comp = zlib.compress(string)

    # Create the necessary directories in .git/objects based on the hash
    if not os.path.isdir(f".git/objects/{sha[:2]}"):
        os.mkdir(f".git/objects/{sha[:2]}")
    
    # If a file with the same hash already exists, remove it
    if os.path.exists(f".git/objects/{sha[:2]}/{sha[2:]}"):
        os.remove(f".git/objects/{sha[:2]}/{sha[2:]}")

    # Write the compressed data to the appropriate file in .git/objects
    with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f2: 
        f2.write(comp)
    return sha
    









   


# def get_tree_files(files):
#     if len(files) == 0:
#         return b""
#     file = files[0]
#     #print(files)
#     string = b""
#     if file != ".git":
#         if os.path.isdir(file):
#             dir_files = os.listdir(file)
#             dir_files = [f"{file}/{f}" for f in dir_files]
#             #print("dir_files: ",dir_files)
#             tree_sequence = get_tree_files(dir_files)
#             print("tree_sequence: ",tree_sequence)
#             header = f"tree {len(tree_sequence)}\0"
#             store = header.encode()+tree_sequence
#             sha = hashlib.sha1(store).hexdigest()

#             #print("store: ",store)
#             comp = zlib.compress(store)

#             # Create the necessary directories in .git/objects based on the hash
#             if not os.path.isdir(f".git/objects/{sha[:2]}"):
#                 os.mkdir(f".git/objects/{sha[:2]}")
            
#             # If a file with the same hash already exists, remove it
#             if os.path.exists(f".git/objects/{sha[:2]}/{sha[2:]}"):
#                 os.remove(f".git/objects/{sha[:2]}/{sha[2:]}")

#             # Write the compressed data to the appropriate file in .git/objects
#             with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f2: 
#                 f2.write(comp)
#             string += f"40000 {file}\0".encode()+sha     
#         else:
#             blob_sha = hash_file(file)   
#             sha = int.to_bytes(int(blob_sha,base=16),length=20,byteorder="big")      
#             file_stat = os.stat(file)
#             is_executable = file_stat.st_mode & stat.S_IXUSR != 0
#             mode = "100755" if is_executable else "100644"
#             file = file if "/" not in file  else file.split("/")[-1]
#             #print("file",file)
#             string += f"{mode} {file}\0".encode()+sha 

            
#     return string+ get_tree_files(files[1:])


def hash_file(file):
    f = open(file, "rb")  # Open the file in binary read mode
    content = f.read()  # Read the entire content of the file

    # Create the header for the blob object, which includes the type 'blob' and the length of the content
    header = f"blob {len(content)}\0"
    store = header.encode() + content  # Combine the header and the content
    
    # Compute the SHA-1 hash of the header+content
    sha = hashlib.sha1(store).hexdigest()
    #print("store2: ",store)
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
    return sha

# def create_blob_entry(path, write=True):
#     with open(path, "rb") as f:
#         data = f.read()
#     header = f"blob {len(data)}\0".encode("utf-8")
#     store = header + data
#     sha = hashlib.sha1(store).hexdigest()
#     if write:
#         # Create the necessary directories in .git/objects based on the hash
#         if not os.path.isdir(f".git/objects/{sha[:2]}"):
#             os.mkdir(f".git/objects/{sha[:2]}")
        
#         # If a file with the same hash already exists, remove it
#         if os.path.exists(f".git/objects/{sha[:2]}/{sha[2:]}"):
#             os.remove(f".git/objects/{sha[:2]}/{sha[2:]}")
#         with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
#             f.write(zlib.compress(store))
#     return sha

# def write_tree(path: str):
#     if os.path.isfile(path):
#         return create_blob_entry(path)
#     contents = sorted(
#         os.listdir(path),
#         key=lambda x: x if os.path.isfile(os.path.join(path, x)) else f"{x}/",
#     )
#     s = b""
#     for item in contents:
#         if item == ".git":
#             continue
#         full = os.path.join(path, item)
#         if os.path.isfile(full):
#             s += f"100644 {item}\0".encode()
#         else:
#             s += f"40000 {item}\0".encode()
#         sha1 = int.to_bytes(int(write_tree(full), base=16), length=20, byteorder="big")
#         s += sha1
#     print("s: ",s)

#     s = f"tree {len(s)}\0".encode() + s
#     sha1 = hashlib.sha1(s).hexdigest()
#      # If a file with the same hash already exists, remove it
#     # Create the necessary directories in .git/objects based on the hash
#     if not os.path.isdir(f".git/objects/{sha1[:2]}"):
#         os.mkdir(f".git/objects/{sha1[:2]}")
    
#     # If a file with the same hash already exists, remove it
#     if os.path.exists(f".git/objects/{sha1[:2]}/{sha1[2:]}"):
#         os.remove(f".git/objects/{sha1[:2]}/{sha1[2:]}")
   
#     with open(f".git/objects/{sha1[:2]}/{sha1[2:]}", "wb") as f:
#         f.write(zlib.compress(s))
#     return sha1



if __name__ == "__main__":
    main()
