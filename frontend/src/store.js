// store.js
import { writable } from 'svelte/store';
import Home from './pages/Home.svelte';

// Store the component constructor (either Home or Setting)
export const myVariable = writable(Home);  // Default to Home
