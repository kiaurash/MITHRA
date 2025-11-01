# Installing RAG Dependencies on Windows

The RAG knowledge base uses ChromaDB, which requires a C++ compiler on Windows.

---

## Option 1: Install Microsoft C++ Build Tools (Recommended)

1. Download **Microsoft C++ Build Tools**: https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. Run the installer and select:
   - ✅ **Desktop development with C++**
   - ✅ **MSVC v143 - VS 2022 C++ x64/x86 build tools**
   - ✅ **Windows 10/11 SDK**

3. After installation, restart your terminal and run:
   ```bash
   cd your_workspace/data/scripts
   pip install -r requirements.txt
   ```

---

## Option 2: Use Pre-built ChromaDB Wheel

Try installing a pre-built wheel that doesn't require compilation:

```bash
pip install chromadb --prefer-binary
```

---

## Option 3: Use Alternative (Simple Python Implementation)

If you can't install ChromaDB, I can create a simple Python-based vector store that works without compilation:

**Pros**:
- No C++ compiler needed
- Works immediately on any platform
- Simpler code

**Cons**:
- Slower than ChromaDB (but fine for <1000 documents)
- Basic functionality only

Let me know if you want me to create this alternative!

---

## Option 4: Use Docker (Advanced)

Run ChromaDB in a Docker container:

```bash
docker run -d -p 8000:8000 chromadb/chroma
```

Then modify scripts to connect to `http://localhost:8000` instead of local storage.

---

## Verifying Installation

Once dependencies are installed, verify with:

```bash
python -c "import chromadb; print('ChromaDB installed successfully!')"
```

---

## What Would You Like To Do?

1. **Install Build Tools** (15-20 min, then ChromaDB will work)
2. **Try pre-built wheel** (quick, may work)
3. **Use simple Python implementation** (I'll create it now, 5 min)
4. **Docker** (if you have Docker installed)
5. **Skip RAG for now** (focus on other Sprint 1 tasks)

Let me know your preference!
