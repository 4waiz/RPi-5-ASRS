import { writable } from 'svelte/store';

export const alertsData = writable([]);
export const diagnosticOptions = writable([]);
export const currentFilter = writable('all');
