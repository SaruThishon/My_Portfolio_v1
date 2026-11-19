/** Shared API response types — mirrors backend Pydantic schemas */

export interface Profile {
  id: string;
  full_name: string;
  professional_title: string;
  hero_headline: string;
  hero_description: string;
  about_bio: string;
  profile_image_url: string | null;
  location: string | null;
  is_available: boolean;
  availability_text: string;
  is_online_public: boolean;
  email: string | null;
  github_url: string | null;
  linkedin_url: string | null;
  twitter_url: string | null;
  website_url: string | null;
  extra_social_links: Record<string, string>;
  updated_at: string;
}

export interface ProjectImage {
  id: string;
  url: string;
  alt_text: string;
  display_order: number;
}

export interface Project {
  id: string;
  title: string;
  slug: string;
  short_description: string;
  description: string;
  problem_statement: string | null;
  solution: string | null;
  architecture_notes: string | null;
  challenges: string | null;
  results: string | null;
  category: string;
  thumbnail_url: string | null;
  github_url: string | null;
  demo_url: string | null;
  technologies: string[];
  status: 'draft' | 'published';
  is_featured: boolean;
  display_order: number;
  seo_title: string | null;
  seo_description: string | null;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  images: ProjectImage[];
}

export interface Skill {
  id: string;
  name: string;
  category: string;
  description: string | null;
  proficiency: string | null;
  icon_url: string | null;
  icon_name: string | null;
  is_visible: boolean;
  display_order: number;
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
  grade: string | null;
  display_order: number;
}

export interface Experience {
  id: string;
  organization: string;
  position: string;
  employment_type: string;
  location: string | null;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
  technologies: string[];
  org_url: string | null;
  logo_url: string | null;
  is_remote: boolean;
  display_order: number;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string;
  issue_date: string | null;
  expiry_date: string | null;
  credential_url: string | null;
  description: string | null;
  display_order: number;
}

export interface Resume {
  id: string;
  original_filename: string;
  file_url: string;
  file_size: number;
  version: number;
  is_active: boolean;
  label: string | null;
  uploaded_at: string;
}

export interface EnquirySubmit {
  name: string;
  email: string;
  subject: string;
  enquiry_type: string;
  message: string;
}
