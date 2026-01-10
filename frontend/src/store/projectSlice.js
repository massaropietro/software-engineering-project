import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    projectName: "",
    description: "",
    repoUrl: "",
    zipFile: null,
};

export const projectSlice = createSlice({
    name: 'project',
    initialState,
    reducers: {
        updateFormData: (state, action) => {
            const { projectName, description, repoUrl, zipFile } = action.payload;
            state.projectName = projectName;
            state.description = description;
            state.repoUrl = repoUrl;
            if (zipFile !== undefined) {
                state.zipFile = zipFile;
            }
        },
        resetForm: () => initialState
    },
});

export const { updateFormData, resetForm } = projectSlice.actions;
export default projectSlice.reducer;
