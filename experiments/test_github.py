from github import Github
import os
import dotenv

dotenv.load_dotenv()

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USER = "pamudu123" 

# Validate token before proceeding
if not GITHUB_TOKEN:
    print("❌ Error: GITHUB_TOKEN environment variable is not set.")
    print("   Please set it with: export GITHUB_TOKEN='your_token_here'")
    exit(1)

if GITHUB_TOKEN == "your_token_here":
    print("❌ Error: GITHUB_TOKEN is still a placeholder.")
    print("   Replace it with your actual GitHub personal access token.")
    exit(1)

try:
    g = Github(GITHUB_TOKEN)
    # Test authentication
    user = g.get_user()
    print(f"✅ Authentication successful! Logged in as: {user.login}")
except Exception as auth_error:
    print(f"❌ Authentication failed: {auth_error}")
    print("   Ensure your GITHUB_TOKEN is valid and has repo access.")
    exit(1)

# --- THE LOGIC TO TEST ---

def test_search_logic():
    print("\n🔍 TEST 1: Searching for 'agent' repos...")
    try:
        query = f"user:{USER} agent in:name"
        repos = g.search_repositories(query=query)
        
        print(f"   Query: {query}")
        print(f"   Total results: {repos.totalCount}")
        
        if repos.totalCount == 0:
            print("   ⚠️ No repos with 'agent' in name found.")
            print("   Trying alternative: fetching all repos...")
            # Fallback: get all repos for the user
            all_repos = g.get_user(USER).get_repos()
            if all_repos.totalCount > 0:
                first_repo = all_repos[0]
                print(f"   ✅ Using first repo instead: {first_repo.name}")
                return first_repo.name
            else:
                print("   ❌ User has no repositories.")
                return None
        
        found_repos = []
        for repo in repos[:3]:
            print(f"   ✅ Found: {repo.name}")
            found_repos.append(repo.name)
        
        return found_repos[0] if found_repos else None
    except Exception as e:
        print(f"   ❌ Error during search: {e}")
        return None

def test_structure_logic(repo_name):
    print(f"\n📂 TEST 2: Listing files in '{repo_name}'...")
    try:
        repo = g.get_user(USER).get_repo(repo_name)
        contents = repo.get_contents("")
        
        found_files = []
        for file in contents:
            icon = "📁" if file.type == "dir" else "📄"
            print(f"   {icon} {file.path}")
            if file.type == "file":
                found_files.append(file.path)
                
        return found_files
    except Exception as e:
        print(f"   ❌ Error listing files: {e}")
        return []

def test_read_logic(repo_name, file_path):
    print(f"\n📖 TEST 3: Reading content of '{file_path}'...")
    try:
        repo = g.get_user(USER).get_repo(repo_name)
        file_content = repo.get_contents(file_path)
        content = file_content.decoded_content.decode("utf-8")
        
        print("   --- Content Snippet (First 200 chars) ---")
        print(f"   {content[:200]}...")
        print("   -----------------------------------------")
        print("   ✅ Success!")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")

# --- RUN THE TEST ---
if __name__ == "__main__":
    print(f"🚀 Starting Test for User: {USER}\n")
    
    # 1. Search
    target_repo = test_search_logic()
    
    if target_repo:
        # 2. List Files
        files = test_structure_logic(target_repo)
        
        # 3. Read specific file
        target_file = "README.md" 
        if target_file in files:
            test_read_logic(target_repo, target_file)
        elif files:
            test_read_logic(target_repo, files[0])
        else:
            print("   ⚠️ Repo is empty, cannot test reading.")
    else:
        print("\n❌ Tests incomplete. Fix authentication or search parameters above.")