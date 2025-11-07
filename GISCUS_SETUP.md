# Setting Up Comments & Likes for Your Blog

This guide will help you set up Giscus for comments and reactions (likes) on your blog posts.

## Step 1: Enable GitHub Discussions

1. Go to your repository: https://github.com/chasekosborne/chasekosborne.github.io
2. Click on **Settings**
3. Scroll down to the **Features** section
4. Check the box next to **Discussions**

## Step 2: Create a Discussion Category

1. Go to the **Discussions** tab in your repository
2. Click **Categories** (or the gear icon)
3. Create a new category called **"Blog Comments"**
4. Choose the format: **Announcement** (this allows only you to create new discussions, but anyone can comment)

## Step 3: Get Your Giscus Configuration

1. Go to https://giscus.app
2. Fill in your repository: `chasekosborne/chasekosborne.github.io`
3. Under "Discussion Category", select **"Blog Comments"**
4. Under "Page ↔️ Discussions Mapping", choose **pathname**
5. Enable **reactions**
6. Copy the `data-repo-id` and `data-category-id` values from the generated script

## Step 4: Update Your Comments Component

1. Open `blog/comments.html`
2. Replace `REPLACE_WITH_YOUR_REPO_ID` with your actual repo ID
3. Replace `REPLACE_WITH_YOUR_CATEGORY_ID` with your actual category ID

## Step 5: Add Comments to Your Blog Posts

Add this line at the end of each blog post's HTML file, just before the closing `</div>` of the article content:

```html
<!-- Comments Section -->
<script>
  fetch('../comments.html')
    .then(response => response.text())
    .then(data => {
      document.querySelector('.article').insertAdjacentHTML('beforeend', data);
    });
</script>
```

Or simply copy and paste the script from `blog/comments.html` directly into each blog post.

## Features You'll Get:

✅ **Comments**: Visitors can leave comments using their GitHub account
✅ **Reactions**: Built-in like/love/thumbs up reactions on comments and the main post
✅ **Reply Threading**: Full threaded conversations
✅ **Markdown Support**: Rich text formatting in comments
✅ **No Backend Needed**: Everything runs through GitHub's infrastructure
✅ **Free**: Completely free to use
✅ **Moderation**: You control the discussions through GitHub

## Optional: Display Comment Counts on Blog Listing

If you want to show comment counts on your main blog page (blog.html), you'll need to use the GitHub API to fetch discussion data. This requires a bit more JavaScript but I can help you implement this if you'd like!

## Notes:

- Visitors need a GitHub account to comment (which is perfect for a technical blog)
- Comments are stored as GitHub Discussions in your repository
- You can moderate comments directly through GitHub
- The system respects your repository's visibility settings

