import { configureStore } from '@reduxjs/toolkit';
import projectReducer from './projectSlice';

export const store = configureStore({
    reducer: {
        project: projectReducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            // Disabilitiamo il check per evitare warning in console salvando oggetti File
            serializableCheck: false,
        }),
});
