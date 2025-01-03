import re

def get_latest_version(changelog_path='/home/ffc/ffchub/fitnessFriendsChallenge/CHANGELOG.md'):
    with open(changelog_path, 'r') as file:
        content = file.read()
    
    # Regex to find the version number
    version_pattern = re.compile(r'\d{2}-\d{2}-\d{4} (\d+\.\d+\.\d+)')
    versions = version_pattern.findall(content)
    
    if versions:
        return versions[0]  # Return the latest version
    return '0.0.0'  # Default version if none found
