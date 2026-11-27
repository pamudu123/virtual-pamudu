// Static identity shown in the page chrome. Everything the assistant *says*
// comes from the agent's knowledge base; this is only the frame around it.

export const AGENT_ID = "virtual_pamudu";

export const profile = {
  name: "Pamudu Ranasinghe",
  initials: "PR",
  headline: "Lead AI Engineer",
  bio: "Building applied ML systems across NLP, computer vision and audio, from research papers to production.",
  focus: ["Agentic RAG", "NLP", "Computer Vision", "Audio ML", "Embedded ML"],
  links: [
    { label: "LinkedIn", href: "https://www.linkedin.com/in/pamudu-ranasinghe/" },
    { label: "GitHub", href: "https://github.com/pamudu123" },
    { label: "Medium", href: "https://medium.com/@pamudu1111" },
    { label: "YouTube", href: "https://www.youtube.com/@pamudu123ranasinghe7/featured" },
    {
      label: "Scholar",
      href: "https://scholar.google.com/citations?hl=en&user=v1CeOs0AAAAJ&view_op=list_works",
    },
  ],
};

export const topics = [
  { label: "Experience", prompt: "Walk me through Pamudu's work experience." },
  { label: "Projects", prompt: "Show me Pamudu's best projects." },
  { label: "Research", prompt: "What research has Pamudu published?" },
  { label: "Skills", prompt: "What are Pamudu's core skills?" },
  { label: "Code", prompt: "Show me his GitHub repositories." },
  { label: "Writing", prompt: "What has Pamudu written about recently?" },
  { label: "Videos", prompt: "Show me his latest YouTube videos." },
  { label: "Get in touch", prompt: "I'd like to get in touch with Pamudu." },
];

export const starterSuggestions = [
  { title: "Who is Pamudu?", message: "Who is Pamudu, in a nutshell?" },
  { title: "Show his best projects", message: "Show me Pamudu's best projects." },
  { title: "What is he working on now?", message: "What is Pamudu working on right now?" },
  { title: "Is he open to collaborating?", message: "I'd like to get in touch with Pamudu about a collaboration." },
];
