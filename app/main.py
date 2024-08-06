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
    elif command == "cat-file": # cats a file from the "objects" folder inside of ".git"
        if sys.argv[2] == "-p":
            file = sys.argv[3]
            with open(f".git/objects/{file[:2]}/{file[2:]}","rb") as f:     # the first two chars are the name of the folder, the rest is the name of the file
                content = zlib.decompress(f.read())         # decompress the content file
                # a blob format after zlib decompression is "blob <size>\0<content>" (example: blob 11\0hello world)
                header, content = content.split(b"\0")  # so we have to split by the "\0"            
                print(content.decode("utf-8"),end="")
                
    elif command == "hash-object":  # Compute the SHA hash of the file + write it to .git/objects
        if sys.argv[2] == "-w":
            file = sys.argv[3]
            f = open(file,"rb") 
            content = f.read()
            header = f"blob {len(content)}\x00"
            store = header.encode("ascii")+content
            blob = hashlib.sha1(store)
            blobHashed = blob.hexdigest()
            comp = zlib.compress(store)
            if not os.path.isdir(f".git/objects/{blobHashed[:2]}"):
                os.mkdir(f".git/objects/{blobHashed[:2]}")
            if os.path.exists(f".git/objects/{blobHashed[:2]}/{blobHashed[2:]}"):
                os.remove(f".git/objects/{blobHashed[:2]}/{blobHashed[2:]}")
            f2 = open(f".git/objects/{blobHashed[:2]}/{blobHashed[2:]}","wb")
            f2.write(comp)
            print(blobHashed)

            f.close()
            f2.close()        
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
