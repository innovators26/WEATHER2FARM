import os

FILE = r"src\dashboard\static\js\tabs\advisory.js"
with open(FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Add an error container below the Generate button
# <button id="genAdvBtn"...
# </button>
code = code.replace(
    '</button>',
    '</button>\n            <div id="advErrorMsg" style="display:none; color:var(--danger); font-size:13px; margin-top:8px; text-align:center;"></div>'
)

# Hide error when generating starts
hide_err = """
    // Hide previous result
    document.getElementById('advResultCard').style.display = 'none';
    document.getElementById('advChatCard').style.display = 'none';
    const errMsg = document.getElementById('advErrorMsg');
    if (errMsg) errMsg.style.display = 'none';
"""
code = code.replace("""
    // Hide previous result
    document.getElementById('advResultCard').style.display = 'none';
    document.getElementById('advChatCard').style.display = 'none';""", hide_err)

# Show error when catch(e) happens
show_err = """    } catch (e) {
      const errMsg = document.getElementById('advErrorMsg');
      if (errMsg) {
        errMsg.innerText = 'Generation failed: ' + e.message;
        errMsg.style.display = 'block';
      }
    }"""
code = code.replace("""    } catch (e) {
      alert('Advisory engine error: ' + e.message);
    }""", show_err)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(code)

print("Patched advisory.js API error handling")
