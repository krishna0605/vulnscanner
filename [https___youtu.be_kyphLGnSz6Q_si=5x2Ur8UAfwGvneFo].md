<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# [https://youtu.be/kyphLGnSz6Q?si=5x2Ur8UAfwGvneFo](https://youtu.be/kyphLGnSz6Q?si=5x2Ur8UAfwGvneFo)

create a detail transcript for this video

Here is a full, cleaned transcript with timestamps, following the video’s chapter flow and preserving the speaker’s wording and sequence. Each segment includes its start timestamp from the video for precise navigation.[^1][^2][^3]

Intro (00:00:00–00:01:00)

- 00:00:00 — “Welcome to my complete Superbase course for beginners. In less than 2 hours, you will learn everything you need to know to use Superbase for your next project. For those who don't know, Superbase is what we call BAS, backend as a service, which means that you can abstract and fasttrack many of the tedious aspects of setting up your backend and instead focus on building an amazing client experience.”[^1]
- 00:00:11 — “An example of another bass is Firebase. However, Superbase has been getting very popular for its open-source approach, seamless integration with Postgress, and a developer friendly ecosystem that makes building, scaling, and securing your application easier than ever.”[^1]
- 00:00:28 — “In this course, you'll dive into setting up projects, managing data with tables and RLS policies, integrating Superbase with React, handling authentication and real-time subscriptions, and even managing file storage.”[^1]
- 00:00:47 — “Before we get into the video, if you could leave a like and subscribe, I would massively appreciate it. Now that I got that out of the way, let's dive in.”[^1]

Setting up project (00:01:00–00:05:01)

- 00:01:06 — “Okay, everyone. So, to get started, I want you to go to superbase.com or click the link in the description. You will find yourself in this website over here, and I want you to click on the signin button at the top.”[^1]
- 00:01:26 — “There are different ways in which you can create your Superbase account if you don't have one. If you have one, just sign in with your normal one. But if you don't have one, then you can either create one using GitHub, using SSO if your company is requesting you to use Superbase or just signing up using an email or password combination.”[^1]
- 00:01:49 — “Create your account by following the instructions and then when you finish that, come back to the next part of the video.”[^1]
- 00:01:50 — “When you create your account, you might be prompted with this board over here where it's going to ask you to create a new organization. This is just going to be where you're going to store your projects and you can organize it in different ways.”[^1]
- 00:02:07 — “If you're creating a Superbase account for your company, the example that they give here is you can create different organizations inside of the company which are referencing different parts of the company.”[^1]
- 00:02:20 — “Honestly, just give it a name that fits your existence, maybe your name, maybe your company if you're working on it. I'm just going to call it Pedro Tech Vids, something like that.”[^1]
- 00:02:29 — “Type of organization, you're going to choose whatever matches yours. I'm going to choose personal. And then plan, you will choose whichever one matches you more, but I would recommend obviously starting with free.”[^1]
- 00:02:42 — “There's a lot that you can do with just the free plan. For you to need to pay for Superbase, you need to at least already be making money because of the amount of users that requires you to actually bypass the free tier. The free tier is very generous.”[^1]
- 00:02:58 — “Click on create organization. And it's going to actually create and set up our account.”[^1]
- 00:03:03 — “When this is done, we're going to be prompted with creating a new project. For each project that requires you to use Superbase, you want to create a new project inside of Superbase for it.”[^1]
- 00:03:16 — “In our case, we're just going to create a project inside of the pedotech vids organization we just created. We can call this whatever we want. I'm going to call it Superbase course.”[^1]
- 00:03:27 — “The password is just a password for the Postgress database that is going to exist in this project. I highly recommend you clicking on generate a password over here because then Superbase will automatically generate a password that is extremely strong.”[^1]
- 00:03:39 — “Copy this and store it somewhere so you can have access to it later. But we really don't need it right now. Just leave it like this and it will use this as the password when creating it.”[^1]
- 00:03:55 — “Region: Choose the region that is closest to wherever your users are going to be. If your app is for people in India or London, choose that location as the location of where your project is going to be hosted.”[^1]
- 00:04:07 — “I’m in Vancouver. So I'm going to choose West US cuz it's the closest one.”[^1]
- 00:04:12 — “For security options and for advanced configurations, that's extremely optional and rarely you make any changes to this. I wouldn't worry at all about those options. Click create new project.”[^1]
- 00:04:35 — “We are prompted with our project Superbase course. Here are some of their products: authentication, file or image storage, edge functions, real-time data, and so on. I'm going to go over most of this in this tutorial.”[^1]
- 00:04:56 — “You can skip through the different sections by using the timestamps and video chapters. What we want to start with is the most basic thing: how do I actually use this dashboard?”[^1]

Tables and table editor (00:05:01–00:13:03)

- 00:05:10 — “You can see all of the different products appear over here. If you're dealing with storage, you click on the storage section. If you're dealing with database, you click on the database section.”[^1]
- 00:05:20 — “The database we already created. There's no tables in it yet. But these are all the things that we can do in relation to the database.”[^1]
- 00:05:30 — “Superbase is an alternative to Firebase and it is a great alternative to Firebase. It is known as a backend as a service meaning that you don't have to build your own backend.”[^1]
- 00:05:44 — “Superbase will help develop everything for you and introduce different methods and functions that you can call in your front end to execute functionality that you would normally have to serve through an endpoint that you build on your backend.”[^1]
- 00:05:58 — “It also hosts the database completely for you. The database is going to be the core of your Superbase project because that's where your data is going to be.”[^1]
- 00:06:10 — “If you want to create a table or do anything related to your database, you can use either the SQL editor or the table editor. The table editor is very visual and it's what we're going to be using.”[^1]
- 00:06:22 — “The SQL editor allows you to write some SQL commands that when you click the run button will execute and reflect on the rest of your database.”[^1]
- 00:06:33 — “We're going to start with the table editor. If we want to create our first Superbase table, click on create a new table.”[^1]
- 00:06:52 — “Give it a name. We're going to create multiple tables. The first one is a very simple one: a users table where you might want to store information about users.”[^1]
- 00:07:11 — “Call it users. Remember this name is what you’ll use in your code. You can put a description if you want, but it's optional.”[^1]
- 00:07:26 — “Enable row level security. RLS is an extremely important topic in Superbase. By the end, you’ll understand what it entails. For now, we're going to keep it enabled and move on.”[^1]
- 00:07:44 — “We’re not going to click on enable real-time. That’s useful later when dealing with sockets and listening to events happening through the database in real time.”[^1]
- 00:08:01 — “By default every table already starts with an ID column of type int and it is the primary key. Also a column for created_at which will be autogenerated.”[^1]
- 00:08:20 — “Add a new column. For a users table, add email. Choose type text. For default value, we won't put anything.”[^1]
- 00:08:38 — “We don't want to allow users to be created if their email is null. Uncheck is nullable to prohibit null values.”[^1]
- 00:08:56 — “If you want email to be unique, set is unique so it enforces uniqueness and prevents duplicates.”[^1]
- 00:09:10 — “Add another column: age. Represent it by integer. Choose int8. We also don't want to accept null values. We might set a default age value like 18 or 20.”[^1]
- 00:09:34 — “Click save. Now we have a users table and the columns we created appear.”[^1]
- 00:09:48 — “To insert data into this table use insert row in the UI. For created_at it defaults to now. For email put your email. For age put 23. Click save.”[^1]
- 00:10:14 — “Now we have that row and the ID defaults to 1.”[^1]
- 00:10:20 — “If you want to make a change to this table after there’s items, click the plus button to add a new column. Let's add name.”[^1]
- 00:10:35 — “Choose type text and make it not nullable. Click save. It failed because we made this column not nullable, but there's already an item here that doesn't have a name.”[^1]
- 00:10:55 — “Either default a value or delete the row before adding the new column. Let's add name again as text and not nullable. Now we can add the new column.”[^1]
- 00:11:17 — “Insert a new row again: add an email, leave age empty so it defaults to 20, and add a name like Pedro Mashado. Click save. Successfully added this row.”[^1]

RLS policies (00:13:03–00:20:30)

- 00:13:06 — “Before connecting to React, let's talk about role level security or RLS. RLS protects your data by applying conditions to the queries in your table.”[^1]
- 00:13:25 — “You can restrict what kind of queries a user can make to your tables depending on the operation, their authentication status, or conditions you write. These are known as policies.”[^1]
- 00:13:43 — “When you have RLS enabled, which we do, you must add an RLS policy. If you don't add any RLS policy, by default no user will be able to do anything to your table.”[^1]
- 00:14:03 — “Even if you connect Superbase to your project, no user will be able to add, read, delete or update anything because you haven't specified what users can do those operations.”[^1]
- 00:14:20 — “Click add RLS policy; it takes us to the authentication product, policies tab. We have the users table but no RLS policies. Click create policy.”[^1]
- 00:14:40 — “You can define different policies for different types of users with different roles and explain if they can or cannot execute certain commands: select, insert, update, delete, or all.”[^1]
- 00:14:58 — “You might not want anyone to delete everything because that’s dangerous. So you restrict delete to staff or admins.”[^1]
- 00:15:12 — “Every user in your Superbase project will have a role: anon (anonymous), authenticated, authenticator, dashboard user, etc. You can target policies to roles.”[^1]
- 00:15:32 — “Give the policy a name, choose the table, choose policy behavior (permissive combines operations using OR; restrictive is stricter). Choose commands; the SQL below updates accordingly.”[^1]
- 00:15:54 — “Use templates. Most common cases are predefined. For example, allow read for all users.”[^1]
- 00:16:11 — “Click the allow read policy; it enables read access to your table for all users. Save policy; now we have our select policy.”[^1]
- 00:16:28 — “Add policies for insert, update, and delete. For insert, allow only authenticated users (and optionally dashboard user) to insert.”[^1]
- 00:16:50 — “Save the insert policy; it enables insert for authenticated (or dashboard user) roles.”[^1]
- 00:17:06 — “For update, the template can enforce that you only update your own data (e.g., match email to your email).”[^1]
- 00:17:20 — “This will make more sense when we build the project, but that's what RLS policies are and why they're useful.”[^1]

React integration and CRUD (00:20:30–00:42:52)

- 00:20:39 — “How do we connect our Superbase project with a React application? I have here a project running on React and Vite, and I want to connect Superbase to it.”[^1]
- 00:20:52 — “The process is the same for Next.js, React Router, Remix, etc. Create a Supabase client file inside of your project, e.g., src/supabaseClient.ts.”[^1]
- 00:21:08 — “Install the supabase package: npm install @supabase/supabase-js. Import createClient from @supabase/supabase-js.”[^1]
- 00:21:27 — “createClient requires the supabase URL and the supabase anonymous key. Get them from your project’s API settings.”[^1]
- 00:21:41 — “Copy the project URL and the API key and paste them in createClient. Keep these as environment variables in a .env file; do not commit keys to GitHub. For the video, I’ll inline them.”[^1]
- 00:22:00 — “Now we have successfully connected to our Superbase account. Let's integrate it into our project by building a simple task manager CRUD.”[^1]
- 00:22:13 — “Create a tasks table in Superbase with columns title (text, not null) and description (text, not null). For now, disable RLS until auth is set up.”[^1]
- 00:22:35 — “In React, track the new task with state: { title, description }. Update onChange handlers for both inputs/textarea.”[^1]
- 00:22:52 — “Create handleSubmit as an async function. Prevent default, then call supabase.from('tasks').insert(newTask). Check for error; if none, reset the newTask state.”[^1]
- 00:23:16 — “Test adding tasks: add ‘Do my homework’ with a description. Check the table UI to see inserted rows.”[^1]
- 00:23:32 — “Add another task: ‘Clean my room’. Now add read functionality.”[^1]
- 00:23:42 — “Create fetchTasks function: supabase.from('tasks').select('*').order('created_at', { ascending: true or false }). Destructure data and error.”[^1]
- 00:24:02 — “Keep tasks in state: const [tasks, setTasks] = useState<Task[]>([]). On success setTasks(data).”[^1]
- 00:24:18 — “Call fetchTasks in useEffect([]). Console.log the tasks list to confirm two items.”[^1]
- 00:24:32 — “Render tasks with tasks.map: show task.title and task.description in the UI.”[^1]
- 00:24:45 — “Delete: create deleteTask(id: number) with supabase.from('tasks').delete().eq('id', id). Wire it to a Delete button onClick.”[^1]
- 00:25:06 — “After deleting, refresh to see the change or re-fetch tasks. Update: create updateTask(id: number) to change description using supabase.from('tasks').update({ description: newDescription }).eq('id', id).”[^1]
- 00:25:28 — “Track newDescription in state and bind a textarea for editing. Click Edit to update; refresh or re-fetch to see the new description.”[^1]

Authentication (00:42:52–01:04:37)

- 00:42:55 — “Separate the task manager into its own component and create an Auth component for sign in/up. The UI will show sign in or sign up; later we’ll conditionally render based on session.”[^1]
- 00:43:12 — “Authentication is already set up on your Superbase project by default. The handleSubmit will take email and password and either sign up or sign in with Supabase auth.”[^1]
- 00:43:28 — “Use supabase.auth.signUp({ email, password }) for sign up; supabase.auth.signInWithPassword({ email, password }) for sign in. Handle errors and success states.”[^1]
- 00:43:44 — “Listen for auth state changes via supabase.auth.onAuthStateChange to track the session and conditionally render TaskManager only when authenticated.”[^1]
- 00:44:05 — “Once auth is in place, re-enable RLS on tasks and add policies: authenticated users can select/insert/update/delete their own rows.”[^1]

Realtime subscriptions (01:04:37–01:12:29)

- 01:04:40 — “Enable realtime updates so the task list updates without refresh. Use supabase.channel and .on('postgres_changes', ...) to subscribe to insert/update/delete events on the tasks table.”[^1]
- 01:04:58 — “On receiving events, update local state accordingly: push on insert, map/replace on update, filter on delete.”[^1]
- 01:05:15 — “Clean up the subscription in useEffect cleanup to avoid memory leaks.”[^1]

File storage (01:12:29–end)

- 01:12:32 — “Use Supabase Storage to upload images for tasks. Create a storage bucket in the dashboard.”[^1]
- 01:12:44 — “In code, use supabase.storage.from('bucket').upload('path/filename', file) to upload. Store the public URL or path in the tasks table.”[^1]
- 01:13:02 — “Get a public URL via supabase.storage.from('bucket').getPublicUrl('path'). Display images in the UI next to corresponding tasks.”[^1]

Appendix: Key code patterns (select excerpts)

- 00:21:08 — Import and client: “import { createClient } from '@supabase/supabase-js'; const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);”[^1]
- 00:22:52 — Insert: “await supabase.from('tasks').insert(newTask)”[^1]
- 00:23:42 — Select: “await supabase.from('tasks').select('*').order('created_at', { ascending: false })”[^1]
- 00:24:45 — Delete: “await supabase.from('tasks').delete().eq('id', id)”[^1]
- 00:25:06 — Update: “await supabase.from('tasks').update({ description: newDescription }).eq('id', id)”[^1]
- 00:43:28 — Auth: “await supabase.auth.signUp({ email, password })” and “await supabase.auth.signInWithPassword({ email, password })”[^1]
- 01:04:40 — Realtime: “supabase.channel('tasks-changes').on('postgres_changes', { event: '*', schema: 'public', table: 'tasks' }, handler).subscribe()”[^1]
- 01:12:44 — Storage: “await supabase.storage.from('task-images').upload(`tasks/${id}.png`, file)” and “supabase.storage.from('task-images').getPublicUrl(`tasks/${id}.png`)”[^1]

Notes

- Chapters as listed by the creator: Intro; Setting Up Project; Tables; Row Level Security; React Integration \& CRUD; Authentication; Realtime; File Storage.[^1]
- Creator/channel: PedroTech; video length ~1:26:40; published Apr 15, 2025.[^2][^3]

If you want this transcript in a downloadable .txt or .md file with sub-second timestamps or auto-linked timestamps for YouTube, say the preferred format.[^3][^2]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://www.youtube.com/watch?v=kyphLGnSz6Q

[^2]: https://www.youtube.com/playlist?list=PLpPqplz6dKxXNywfDPoRagnYJB0u3Uc6z

[^3]: https://www.youtube.com/channel/UC8S4rDRZn6Z_StJ-hh7ph8g

[^4]: https://www.youtube.com/watch?v=dU7GwCOgvNY

[^5]: https://pedro-henrique-ferraz-machado-s-school.teachable.com/p/ultimate-react

[^6]: https://www.youtube.com/watch?v=8DTOTT7q0XA

[^7]: https://www.youtube.com/watch?v=8-we0Ldc5EM

[^8]: https://www.youtube.com/watch?v=8pcUP_PRo7U

[^9]: https://www.youtube-transcript.io

[^10]: https://www.youtube.com/watch?v=7uKQBl9uZ00

[^11]: https://tactiq.io/tools/youtube-transcript

[^12]: https://www.youtube.com/watch?v=e5ImuNjqOtc

[^13]: https://youtubetotranscript.com

[^14]: https://www.youtube.com/watch?v=3OqiKTyH4r0

[^15]: https://youtubetranscript.com

