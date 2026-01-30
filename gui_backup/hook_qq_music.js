const TARGET_DLL = "QQMusicCommon.dll";

console.log("[INFO] Loading QQ Music Decryption Script");

// Get all function addresses
var EncAndDesMediaFileConstructorAddr = Module.findExportByName(TARGET_DLL, "??0EncAndDesMediaFile@@QAE@XZ");
var EncAndDesMediaFileDestructorAddr = Module.findExportByName(TARGET_DLL, "??1EncAndDesMediaFile@@QAE@XZ");
var EncAndDesMediaFileOpenAddr = Module.findExportByName(TARGET_DLL, "?Open@EncAndDesMediaFile@@QAE_NPB_W_N1@Z");
var EncAndDesMediaFileGetSizeAddr = Module.findExportByName(TARGET_DLL, "?GetSize@EncAndDesMediaFile@@QAEKXZ");
var EncAndDesMediaFileReadAddr = Module.findExportByName(TARGET_DLL, "?Read@EncAndDesMediaFile@@QAEKPAEK_J@Z");

console.log("[INFO] Function addresses retrieved");

// Create NativeFunction
var EncAndDesMediaFileConstructor = new NativeFunction(EncAndDesMediaFileConstructorAddr, "pointer", ["pointer"], "thiscall");
var EncAndDesMediaFileDestructor = new NativeFunction(EncAndDesMediaFileDestructorAddr, "void", ["pointer"], "thiscall");
var EncAndDesMediaFileOpen = new NativeFunction(EncAndDesMediaFileOpenAddr, "bool", ["pointer", "pointer", "bool", "bool"], "thiscall");
var EncAndDesMediaFileGetSize = new NativeFunction(EncAndDesMediaFileGetSizeAddr, "uint32", ["pointer"], "thiscall");
var EncAndDesMediaFileRead = new NativeFunction(EncAndDesMediaFileReadAddr, "uint", ["pointer", "pointer", "uint32", "uint64"], "thiscall");

console.log("[INFO] NativeFunction wrappers created");

rpc.exports = {
  decrypt: function (srcFileName, tmpFileName) {
    console.log("[START] Decrypting: " + srcFileName);
    
    try {
      // Allocate object memory
      var EncAndDesMediaFileObject = Memory.alloc(0x28);
      console.log("[STEP 1] Object memory allocated");
      
      // Call constructor
      console.log("[STEP 2] Calling constructor...");
      EncAndDesMediaFileConstructor(EncAndDesMediaFileObject);
      console.log("[STEP 2] Constructor called");
      
      // Prepare filename
      var fileNameUtf16 = Memory.allocUtf16String(srcFileName);
      console.log("[STEP 3] Filename allocated");
      
      // Call Open method
      console.log("[STEP 4] Calling Open method...");
      var openResult = EncAndDesMediaFileOpen(EncAndDesMediaFileObject, fileNameUtf16, 1, 0);
      console.log("[STEP 4] Open method returned: " + openResult);
      
      if (!openResult) {
        console.log("[ERROR] Open method failed!");
        EncAndDesMediaFileDestructor(EncAndDesMediaFileObject);
        return "Open failed";
      }
      
      // Get file size
      console.log("[STEP 5] Calling GetSize method...");
      var fileSize = EncAndDesMediaFileGetSize(EncAndDesMediaFileObject);
      console.log("[STEP 5] File size: " + fileSize);
      
      if (fileSize == 0 || fileSize > 100 * 1024 * 1024) {
        console.log("[ERROR] Invalid file size: " + fileSize);
        EncAndDesMediaFileDestructor(EncAndDesMediaFileObject);
        return "Invalid file size: " + fileSize;
      }
      
      // Create output file
      console.log("[STEP 6] Creating output file...");
      var tmpFile = new File(tmpFileName, "wb");
      
      // Read file content in chunks
      console.log("[STEP 7] Starting chunked file reading...");
      var chunkSize = 0x10000; // Read 64KB at a time
      var bytesRead = 0;
      var buffer = Memory.alloc(chunkSize);
      
      while (bytesRead < fileSize) {
        var remaining = fileSize - bytesRead;
        var currentChunk = chunkSize < remaining ? chunkSize : remaining;
        
        // Read current chunk
        var readResult = EncAndDesMediaFileRead(EncAndDesMediaFileObject, buffer, currentChunk, bytesRead);
        
        if (readResult <= 0) {
          console.log("[ERROR] Read failed at offset: " + bytesRead);
          break;
        }
        
        // Write current chunk to file
        var chunkData = buffer.readByteArray(readResult);
        tmpFile.write(chunkData);
        
        bytesRead += readResult;
        
        // Output progress every 5MB
        if (bytesRead % (5 * 1024 * 1024) == 0 || bytesRead == fileSize) {
          var progress = (bytesRead / fileSize * 100).toFixed(1);
          console.log("[PROGRESS] " + progress + "% (" + bytesRead + "/" + fileSize + ")");
        }
      }
      
      tmpFile.close();
      
      if (bytesRead != fileSize) {
        console.log("[WARNING] Bytes read mismatch. Expected: " + fileSize + ", Actual: " + bytesRead);
      } else {
        console.log("[SUCCESS] File reading completed. Total bytes: " + bytesRead);
      }
      
      // Call destructor
      console.log("[STEP 8] Calling destructor...");
      EncAndDesMediaFileDestructor(EncAndDesMediaFileObject);
      
      console.log("[FINISHED] Decryption successful!");
      return "Success - Read " + bytesRead + " bytes";
      
    } catch (e) {
      console.log("[EXCEPTION] " + e.toString());
      return "Exception: " + e.toString();
    }
  }
};

console.log("[INFO] Decryption script loaded successfully");