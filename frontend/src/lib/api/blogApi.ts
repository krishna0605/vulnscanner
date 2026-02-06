'use client';

// ================================================
// BLOG AGGREGATOR - Configure your usernames here
// ================================================
export const BLOG_CONFIG = {
  devto: {
    enabled: true,
    username: 'vulnscanner', // Change to your Dev.to username
  },
  medium: {
    enabled: true,
    username: 'vulnscanner', // Change to your Medium username (without @)
  },
  hashnode: {
    enabled: true,
    host: 'vulnscanner.hashnode.dev', // Change to your Hashnode blog URL
  },
};

// ================================================
// Types
// ================================================
export interface BlogPost {
  id: string;
  title: string;
  excerpt: string;
  coverImage: string;
  author: string;
  authorAvatar: string;
  date: string;
  readTime: string;
  category: string;
  tags: string[];
  url: string;
  source: 'devto' | 'medium' | 'hashnode';
  sourceIcon: string;
}

export interface BlogCategory {
  id: string;
  name: string;
  count: number;
}

// ================================================
// Dev.to API
// ================================================
async function fetchDevTo(): Promise<BlogPost[]> {
  if (!BLOG_CONFIG.devto.enabled) return [];
  
  try {
    const res = await fetch(
      `https://dev.to/api/articles?username=${BLOG_CONFIG.devto.username}&per_page=20`,
      { next: { revalidate: 3600 } } // Cache for 1 hour
    );
    
    if (!res.ok) return [];
    
    const articles = await res.json();
    
    return articles.map((article: any) => ({
      id: `devto-${article.id}`,
      title: article.title,
      excerpt: article.description || '',
      coverImage: article.cover_image || article.social_image || '',
      author: article.user?.name || BLOG_CONFIG.devto.username,
      authorAvatar: article.user?.profile_image || '',
      date: new Date(article.published_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      }),
      readTime: `${article.reading_time_minutes} min read`,
      category: article.tag_list?.[0] || 'General',
      tags: article.tag_list || [],
      url: article.url,
      source: 'devto' as const,
      sourceIcon: 'code',
    }));
  } catch (error) {
    console.error('Dev.to fetch error:', error);
    return [];
  }
}

// ================================================
// Medium RSS (via rss2json API)
// ================================================
async function fetchMedium(): Promise<BlogPost[]> {
  if (!BLOG_CONFIG.medium.enabled) return [];
  
  try {
    const rssUrl = `https://medium.com/feed/@${BLOG_CONFIG.medium.username}`;
    const res = await fetch(
      `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(rssUrl)}`,
      { next: { revalidate: 3600 } }
    );
    
    if (!res.ok) return [];
    
    const data = await res.json();
    if (data.status !== 'ok') return [];
    
    return data.items.map((item: any, index: number) => {
      // Extract first image from content
      const imgMatch = item.content?.match(/<img[^>]+src="([^">]+)"/);
      const coverImage = imgMatch ? imgMatch[1] : '';
      
      // Extract categories
      const categories = item.categories || [];
      
      // Estimate read time (200 words per minute)
      const wordCount = item.content?.split(/\s+/).length || 0;
      const readTime = Math.max(1, Math.ceil(wordCount / 200));
      
      return {
        id: `medium-${index}`,
        title: item.title,
        excerpt: item.description?.replace(/<[^>]*>/g, '').slice(0, 150) + '...',
        coverImage,
        author: item.author || BLOG_CONFIG.medium.username,
        authorAvatar: '',
        date: new Date(item.pubDate).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        }),
        readTime: `${readTime} min read`,
        category: categories[0] || 'Article',
        tags: categories,
        url: item.link,
        source: 'medium' as const,
        sourceIcon: 'article',
      };
    });
  } catch (error) {
    console.error('Medium fetch error:', error);
    return [];
  }
}

// ================================================
// Hashnode GraphQL API
// ================================================
async function fetchHashnode(): Promise<BlogPost[]> {
  if (!BLOG_CONFIG.hashnode.enabled) return [];
  
  try {
    const query = `
      query GetPosts($host: String!) {
        publication(host: $host) {
          posts(first: 20) {
            edges {
              node {
                id
                title
                brief
                slug
                coverImage { url }
                author { name profilePicture }
                publishedAt
                readTimeInMinutes
                tags { name }
              }
            }
          }
        }
      }
    `;
    
    const res = await fetch('https://gql.hashnode.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        variables: { host: BLOG_CONFIG.hashnode.host },
      }),
      next: { revalidate: 3600 },
    });
    
    if (!res.ok) return [];
    
    const data = await res.json();
    const posts = data?.data?.publication?.posts?.edges || [];
    
    return posts.map((edge: any) => {
      const post = edge.node;
      return {
        id: `hashnode-${post.id}`,
        title: post.title,
        excerpt: post.brief || '',
        coverImage: post.coverImage?.url || '',
        author: post.author?.name || 'Author',
        authorAvatar: post.author?.profilePicture || '',
        date: new Date(post.publishedAt).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        }),
        readTime: `${post.readTimeInMinutes || 5} min read`,
        category: post.tags?.[0]?.name || 'Blog',
        tags: post.tags?.map((t: any) => t.name) || [],
        url: `https://${BLOG_CONFIG.hashnode.host}/${post.slug}`,
        source: 'hashnode' as const,
        sourceIcon: 'tag',
      };
    });
  } catch (error) {
    console.error('Hashnode fetch error:', error);
    return [];
  }
}

// ================================================
// Main Aggregator Function
// ================================================
export async function getAllBlogs(): Promise<BlogPost[]> {
  const [devtoPosts, mediumPosts, hashnodePosts] = await Promise.all([
    fetchDevTo(),
    fetchMedium(),
    fetchHashnode(),
  ]);
  
  // Merge all posts
  const allPosts = [...devtoPosts, ...mediumPosts, ...hashnodePosts];
  
  // Sort by date (newest first)
  allPosts.sort((a, b) => {
    const dateA = new Date(a.date).getTime();
    const dateB = new Date(b.date).getTime();
    return dateB - dateA;
  });
  
  return allPosts;
}

export function getCategories(posts: BlogPost[]): BlogCategory[] {
  const categoryMap = new Map<string, number>();
  
  posts.forEach((post) => {
    const count = categoryMap.get(post.category) || 0;
    categoryMap.set(post.category, count + 1);
  });
  
  return Array.from(categoryMap.entries())
    .map(([name, count]) => ({
      id: name.toLowerCase().replace(/\s+/g, '-'),
      name,
      count,
    }))
    .sort((a, b) => b.count - a.count);
}

export function filterBySource(posts: BlogPost[], source: string | null): BlogPost[] {
  if (!source || source === 'all') return posts;
  return posts.filter((post) => post.source === source);
}

export function filterByCategory(posts: BlogPost[], category: string | null): BlogPost[] {
  if (!category || category === 'all') return posts;
  return posts.filter((post) => 
    post.category.toLowerCase() === category.toLowerCase() ||
    post.tags.some(tag => tag.toLowerCase() === category.toLowerCase())
  );
}

export function paginatePosts(posts: BlogPost[], page: number, perPage: number = 6): {
  posts: BlogPost[];
  totalPages: number;
  currentPage: number;
} {
  const start = (page - 1) * perPage;
  const paginatedPosts = posts.slice(start, start + perPage);
  
  return {
    posts: paginatedPosts,
    totalPages: Math.ceil(posts.length / perPage),
    currentPage: page,
  };
}
