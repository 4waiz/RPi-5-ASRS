// store.js
import { writable } from 'svelte/store';
import Home from './Pages/Home.svelte';
import Setting from './Pages/Setting.svelte';
import Alerts from './Pages/Alerts.svelte';

// Store the component constructor (either Home or Setting)
export const myVariable = writable(Home);  // Default to Home
