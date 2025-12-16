// store.js
import { writable } from 'svelte/store';

// Store page names instead of component references
export const currentPage = writable('Home');  // Default to Home

export let ActiveTapHomePag = writable(0);

export const curentMode = writable('Live');

export const isModePopupOpen = writable(false);

export const isPassWordPopupOpen = writable(false);

export const USER_TOKEN = writable(''); 