from gitmcp import search_my_repos, get_file_structure, read_file_content

# Test Tool 1: Search
print("=" * 50)
print("Testing search_my_repos...")
result = search_my_repos("agent")
print(result)

# Test Tool 2: File Structure (replace with actual repo name)
print("\n" + "=" * 50)
print("Testing get_file_structure...")
result = get_file_structure("your-repo-name")
print(result)

# Test Tool 3: Read File (replace with actual repo and file)
print("\n" + "=" * 50)
print("Testing read_file_content...")
result = read_file_content("your-repo-name", "README.md")
print(result[:200])  # First 200 chars
