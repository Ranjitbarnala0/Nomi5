
import { StatusBar } from 'expo-status-bar';
import { SimulationProvider } from './src/core/context';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <SimulationProvider>
      <AppNavigator />
      <StatusBar style="light" />
    </SimulationProvider>
  );
}
