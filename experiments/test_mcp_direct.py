import sys
sys.path.insert(0, '.')

from gitmcp import search_my_repos, get_file_structure, read_file_content, list_all_repos, find_repo_by_name

def test_all_tools():
    print("🧪 Testing MCP Tools\n")
    
    # Test NEW: List all repos
    print("=" * 60)
    print("TEST 0: Listing all your repositories")
    print("=" * 60)
    result = list_all_repos(5)
    print(result)
    
    # Test NEW: Find specific repo
    print("\n" + "=" * 60)
    print("TEST 0.5: Finding specific repository")
    print("=" * 60)
    result = find_repo_by_name("Audio_Engineering")
    print(result)
    
    # Test 1: Search repos
    print("\n" + "=" * 60)
    print("TEST 1: Searching for repos with keyword")
    print("=" * 60)
    result = search_my_repos("Audio_Engineering")
    print(result)
    
    # Test 2: Get file structure
    print("\n" + "=" * 60)
    print("TEST 2: Getting file structure")
    print("=" * 60)
    print("Enter a repo name from above (or press Enter to skip):")
    repo_name = input("> ").strip()
    
    if repo_name:
        result = get_file_structure(repo_name)
        print(result)
        
        # Test 3: Read a file
        print("\n" + "=" * 60)
        print("TEST 3: Reading a file")
        print("=" * 60)
        print("Enter a file path from above (e.g., README.md):")
        file_path = input("> ").strip()
        
        if file_path:
            result = read_file_content(repo_name, file_path)
            print(f"\n--- Content Preview (first 500 chars) ---")
            print(result[:500])
            print(f"\n... (total length: {len(result)} chars)")

if __name__ == "__main__":
    test_all_tools()
