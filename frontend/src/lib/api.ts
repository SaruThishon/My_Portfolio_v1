import type { Profile, Project, Skill, Education, Experience, Certification, Resume, EnquirySubmit } from '../types/api';

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchAPI<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_URL}/api${path}`, {
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) return null;
    return res.json() as Promise<T>;
  } catch {
    return null;
  }
}

export async function getProfile(): Promise<Profile | null> {
  return fetchAPI<Profile>('/profile');
}

export async function getPublishedProjects(): Promise<Project[] | null> {
  return fetchAPI<Project[]>('/projects/public');
}

export async function getProjectBySlug(slug: string): Promise<Project | null> {
  return fetchAPI<Project>(`/projects/public/${slug}`);
}

export async function getSkills(): Promise<Skill[] | null> {
  return fetchAPI<Skill[]>('/skills');
}

export async function getEducation(): Promise<Education[] | null> {
  return fetchAPI<Education[]>('/education');
}

export async function getExperience(): Promise<Experience[] | null> {
  return fetchAPI<Experience[]>('/experience');
}

export async function getCertifications(): Promise<Certification[] | null> {
  return fetchAPI<Certification[]>('/certifications');
}

export async function getActiveResume(): Promise<Resume | null> {
  return fetchAPI<Resume>('/resume/active');
}

export async function submitEnquiry(data: EnquirySubmit): Promise<{ message: string; id: string }> {
  const res = await fetch(`${API_URL}/api/enquiries/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Submission failed');
  }
  return res.json();
}
