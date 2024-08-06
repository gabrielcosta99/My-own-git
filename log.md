## First Exercise
Iniating the repository. No big deal here

## Second Exercise: git cat-file
git cat-file is used to view the type of an object, its size, and its content. Example usage:

```sh  
$ git cat-file -p <blob_sha>
hello world # This is the contents of the blob
```

**I only implement the `git cat-file -p`**

The order of the steps are:
1. Read the contents of the blob object file from the `.git/objects` directory
2. Decompress the contents using Zlib
3. Extract the actual "content" from the decompressed data
4. Print the content to stdout


## Third Exercise: git hash-object

`git hash-object` is used to compute the SHA hash of a Git object. When used with the -w flag, it also writes the object to the .git/objects directory.

Here's an example of using git hash-object:
```sh
  # Create a file with some content
  $ echo "hello world" > test.txt

  # Compute the SHA hash of the file + write it to .git/objects
  $ git hash-object -w test.txt
  3b18e512dba79e4c8300dd08aeb37f8e728b8dad

  # Verify that the file was written to .git/objects
  $ file .git/objects/3b/18e512dba79e4c8300dd08aeb37f8e728b8dad
  .git/objects/3b/18e512dba79e4c8300dd08aeb37f8e728b8dad: zlib compressed data
```

**I only implemented the `git hash-object -w`**

To implement it i did the following:
1. Convert the file into a blob, after Zlib decompression (`blob <size>\0<content>`)
2. Compress the blob using zlib
3. Hash the blob
4. Create the directory, in which the file will be stored (if necessary)
4. Write the data **(the compressed blob)** to the appropriate file in `.git/objects` **(the hashed blob)**
5. Print the hashed blob to the console
