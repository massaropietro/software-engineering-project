import { ref, type Ref } from 'vue';
import type { AxiosError, AxiosResponse } from 'axios';

interface UseApiReturn<T> {
  data: Ref<T | null>;
  error: Ref<AxiosError | null>;
  loading: Ref<boolean>;
  execute: (...args: any[]) => Promise<T | undefined>;
}

/**
 * Generic API composable for handling request states.
 * @param apiFunction The API service function to execute
 */
export function useApi<T>(apiFunction: (...args: any[]) => Promise<AxiosResponse<T>>): UseApiReturn<T> {
  const data = ref<T | null>(null) as Ref<T | null>;
  const error = ref<AxiosError | null>(null);
  const loading = ref(false);

  const execute = async (...args: any[]) => {
    data.value = null;
    error.value = null;
    loading.value = true;

    try {
      const response = await apiFunction(...args);
      data.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    data,
    error,
    loading,
    execute,
  };
}
