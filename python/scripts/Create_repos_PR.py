import os
import requests
import time
from dotenv import load_dotenv

# 通用API请求函数

def github_api_request(method, url, headers, data=None):
    response = getattr(requests, method)(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json() if response.content else None

# 加载GitHub环境变量

def load_github_env():
    load_dotenv()
    github_token = os.getenv('github_token')
    github_owner = os.getenv('github_owner')  # 组织名称
    
    if not all([github_token, github_owner]):
        raise ValueError("请确保.env文件中包含github_token和github_owner字段")
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    return github_token, github_owner, headers

# 验证仓库是否存在

def validate_repository_exists(owner, repo, headers):
    try:
        github_api_request(
            'get',
            f"https://api.github.com/repos/{owner}/{repo}",
            headers
        )
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ 仓库 '{owner}/{repo}' 不存在或您无访问权限")
            return False
        raise

# 创建临时分支（基于main分支并添加差异提交）

def create_temp_branch_with_diff(owner, repo, headers):
    # 获取main分支的最新commit SHA
    branch_data = github_api_request(
        'get',
        f"https://api.github.com/repos/{owner}/{repo}/branches/main",
        headers
    )
    latest_commit_sha = branch_data['commit']['sha']
    
    # 生成临时分支名称
    timestamp = int(time.time())
    temp_branch_name = f"temp-pr-branch-{timestamp}"
    
    # 创建临时分支
    github_api_request(
        'post',
        f"https://api.github.com/repos/{owner}/{repo}/git/refs",
        headers,
        {"ref": f"refs/heads/{temp_branch_name}", "sha": latest_commit_sha}
    )
    
    print(f"✅ 临时分支 '{temp_branch_name}' 创建成功！")
    print(f"🔗 分支基于: main 的最新commit")
    
    # 创建一个空的commit来确保临时分支与main分支有差异
    print("🔄 正在添加差异提交...")
    
    # 获取commit信息
    commit_data = github_api_request(
        'get',
        f"https://api.github.com/repos/{owner}/{repo}/git/commits/{latest_commit_sha}",
        headers
    )
    
    # 创建新的空commit
    new_commit = github_api_request(
        'post',
        f"https://api.github.com/repos/{owner}/{repo}/git/commits",
        headers,
        {
            "message": "Empty commit for PR creation",
            "parents": [latest_commit_sha],
            "tree": commit_data["tree"]["sha"]
        }
    )
    
    # 更新临时分支指向新的commit
    github_api_request(
        'patch',
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{temp_branch_name}",
        headers,
        {"sha": new_commit["sha"], "force": True}
    )
    
    print(f"✅ 已添加差异提交，确保临时分支与main分支有差异")
    return temp_branch_name

# 创建Empty PR

def create_empty_pr(owner, repo, headers, title, head, base, body=""):
    pr_data = github_api_request(
        'post',
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        headers,
        {
            "title": title,
            "head": head,  # 源分支（临时分支，有差异）
            "base": base,  # 目标分支（用户输入）
            "body": body,
            "draft": False,
            "maintainer_can_modify": True
        }
    )
    
    print(f"✅ PR创建成功!")
    print(f"🔗 PR链接: {pr_data['html_url']}")
    print(f"📝 PR标题: {pr_data['title']}")
    print(f"👤 创建者: {pr_data['user']['login']}")
    
    return pr_data

# 获取用户输入的仓库列表

def get_repositories_input():
    print("请输入要创建PR的仓库名称，多个仓库用逗号分隔，回车确认")
    print("例如: repo1,repo2,repo3")
    
    repo_input = input("仓库名称: ").strip()
    if not repo_input:
        raise ValueError("请至少输入一个仓库名称")
    
    # 分割输入的仓库名称
    repos = [repo.strip() for repo in repo_input.split(',')]
    return repos

# 主函数

def main():
    try:
        # 加载GitHub环境变量和请求头
        github_token, github_owner, headers = load_github_env()
        
        print("🌟 GitHub组织多仓库自动创建Empty PR工具")
        print(f"🔧 当前组织: {github_owner}")
        
        # 获取用户输入的仓库列表
        repositories = get_repositories_input()
        
        # 获取通用PR信息
        title = input("\n请输入PR标题: ")
        target_branch = input("请输入要合并到的目标分支名: ")
        body = input("请输入PR描述 (可选，直接回车跳过): ")
        
        # 为每个仓库创建PR
        for repo in repositories:
            print(f"\n======== 正在处理仓库: {repo} ========")
            
            # 验证仓库是否存在
            if not validate_repository_exists(github_owner, repo, headers):
                print(f"⏭️  跳过仓库 '{repo}'")
                continue
            
            try:
                # 创建临时分支
                print("🔄 正在创建临时分支并添加差异提交...")
                source_branch = create_temp_branch_with_diff(github_owner, repo, headers)
                
                # 创建PR
                create_empty_pr(github_owner, repo, headers, title, source_branch, target_branch, body)
                print(f"✅ 仓库 '{repo}' 的PR创建完成！")
                
            except Exception as e:
                print(f"❌ 处理仓库 '{repo}' 时出错: {e}")
                # 提取更具体的错误信息
                if hasattr(e, 'response') and hasattr(e.response, 'content') and e.response.content:
                    try:
                        error_data = e.response.json()
                        print(f"📋 错误详情: {error_data}")
                    except:
                        pass
                print(f"⏭️  继续处理下一个仓库")
                continue
        
        print("\n🎉 所有仓库处理完成！")
        
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        print("💡 建议检查:")
        print("  1. .env文件中的GitHub信息是否正确")
        print("  2. GitHub Token是否有足够的权限")

if __name__ == "__main__":
    main()
