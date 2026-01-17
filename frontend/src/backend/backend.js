/* This is the file for handling the requests
   to the backend server with axios */
import apiClient from '@/plugins/axios';
import { endpoints } from "@/constants/constants.js";
import { getErrorMessage } from "@/utils/utils";

export const apiCaller = (method, url, data = null) => {
    return apiClient({
        method: method,
        url: url,
        data: data,
    });
};

export const apiWrapper = (requestPromise, { onSuccess, onError, onFinally, loading, setBackendError } = {}) => {
    return requestPromise
        .then(response => {
            if (onSuccess && typeof onSuccess === 'function') {
                onSuccess(response.data);
            }
            return response.data;
        })
        .catch(error => {
            const message = getErrorMessage(error);

            if (setBackendError && typeof setBackendError === 'function') {
                setBackendError(message);
            }

            if (onError && typeof onError === 'function') {
                onError(message);
            }
            throw error;
        })
        .finally(() => {
            if (loading && typeof loading === 'function') {
                loading(false);
            }

            if (onFinally && typeof onFinally === 'function') {
                onFinally();
            }
        });
};

export const getProjects = (callbacks) => {
    return apiWrapper(
        apiCaller('get', endpoints.projects),
        callbacks
    );
};

export const addProjects = (data, callbacks) => {
    let payload = data;

    if (data.zip_file instanceof File) {
        payload = new FormData();
        Object.keys(data).forEach(key => {
            const value = data[key];
            if (value !== null && value !== undefined) {
                payload.append(key, value);
            }
        });
    }

    return apiWrapper(
        apiCaller('post', endpoints.projects, payload),
        callbacks
    );
};
