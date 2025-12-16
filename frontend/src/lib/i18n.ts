import { writable, derived } from 'svelte/store';
import enTranslations from './locales/en.json';
import arTranslations from './locales/ar.json';

type Translations = typeof enTranslations;
type TranslationKey = string;

const translations: Record<'en' | 'ar', Translations> = {
  en: enTranslations,
  ar: arTranslations
};

// Create a writable store for the current language
export const currentLanguage = writable<'en' | 'ar'>('en');

// Helper function to get nested translation value
function getNestedTranslation(obj: any, path: string): string {
  const keys = path.split('.');
  let result = obj;

  for (const key of keys) {
    if (result && typeof result === 'object' && key in result) {
      result = result[key];
    } else {
      return path; // Return key if translation not found
    }
  }

  return typeof result === 'string' ? result : path;
}

// Create a derived store for the translation function
export const t = derived(currentLanguage, ($currentLanguage) => {
  return (key: TranslationKey): string => {
    const translation = translations[$currentLanguage];
    return getNestedTranslation(translation, key);
  };
});

// Function to change language
export function setLanguage(lang: 'en' | 'ar') {
  currentLanguage.set(lang);

  // Update document language only (keep LTR direction)
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lang;
  }
}

// Function to toggle language
export function toggleLanguage() {
  currentLanguage.update(lang => {
    const newLang = lang === 'en' ? 'ar' : 'en';
    setLanguage(newLang);
    return newLang;
  });
}