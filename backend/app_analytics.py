"""
Analytics API with ML-based forecasting and real-time KPI tracking
Uses scikit-learn for linear regression models and historical data analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json

app = FastAPI(title="Analytics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# DATA MODELS
# ===========================

class HistoricalDataPoint(BaseModel):
    timestamp: str
    value: float

class KPIData(BaseModel):
    current: float
    target: float
    trend: str
    history: List[float]

class ComponentForecast(BaseModel):
    name: str
    color: str
    current_stock: int
    weekly_usage: List[int]
    predicted_usage: List[float]
    recommended_order: int
    reorder_point: int
    lead_time_days: int
    trend_percentage: float
    confidence_score: float
    components: Dict[str, int]
    unit_cost: float
    weeks_of_stock: float
    order_urgency: str  # 'critical', 'soon', 'ok'
    order_by_date: str
    total_predicted_usage: float

class AIInsight(BaseModel):
    type: str
    severity: str
    title: str
    message: str
    confidence: int
    action: str

class AnalyticsResponse(BaseModel):
    kpis: Dict[str, KPIData]
    aiInsights: List[AIInsight]
    inventoryForecast: Dict[str, List[ComponentForecast]]
    timestamp: str
    model_info: Dict[str, Any]


# ===========================
# HISTORICAL DATA GENERATION
# ===========================

class HistoricalDataGenerator:
    """Generates realistic historical data with trends, seasonality, and noise"""

    def __init__(self, seed=42):
        np.random.seed(seed)

    def generate_time_series(
        self,
        days: int = 90,
        base_value: float = 100,
        trend: float = 0.02,
        seasonality_amplitude: float = 10,
        noise_level: float = 5,
        seasonality_period: int = 7
    ) -> List[float]:
        """Generate realistic time series data with trend, seasonality, and noise"""

        timestamps = np.arange(days)

        # Linear trend component
        trend_component = base_value + (timestamps * trend)

        # Seasonal component (weekly pattern)
        seasonal_component = seasonality_amplitude * np.sin(2 * np.pi * timestamps / seasonality_period)

        # Random noise
        noise = np.random.normal(0, noise_level, days)

        # Combine components
        data = trend_component + seasonal_component + noise

        # Ensure non-negative values
        data = np.maximum(data, 0)

        return data.tolist()

    def generate_kpi_history(self, kpi_type: str, hours: int = 24) -> List[float]:
        """Generate KPI-specific historical data"""

        configs = {
            'throughput': {
                'base_value': 230,
                'trend': 0.5,
                'seasonality_amplitude': 20,
                'noise_level': 8
            },
            'availability': {
                'base_value': 93,
                'trend': 0.03,
                'seasonality_amplitude': 2,
                'noise_level': 1
            },
            'inventory_accuracy': {
                'base_value': 97.5,
                'trend': 0.02,
                'seasonality_amplitude': 1,
                'noise_level': 0.5
            },
            'cycle_time': {
                'base_value': 13,
                'trend': -0.03,
                'seasonality_amplitude': 1.5,
                'noise_level': 0.5
            },
            'picking_accuracy': {
                'base_value': 98.5,
                'trend': 0.02,
                'seasonality_amplitude': 0.8,
                'noise_level': 0.3
            },
            'energy_per_cycle': {
                'base_value': 2.6,
                'trend': -0.01,
                'seasonality_amplitude': 0.3,
                'noise_level': 0.1
            },
            'error_rate': {
                'base_value': 3.8,
                'trend': -0.05,
                'seasonality_amplitude': 0.8,
                'noise_level': 0.3
            }
        }

        config = configs.get(kpi_type, configs['throughput'])

        return self.generate_time_series(
            days=hours,
            base_value=config['base_value'],
            trend=config['trend'],
            seasonality_amplitude=config['seasonality_amplitude'],
            noise_level=config['noise_level'],
            seasonality_period=12  # 12-hour cycle for hourly data
        )


# ===========================
# ML FORECASTING MODELS
# ===========================

class InventoryForecastModel:
    """Linear regression model for inventory forecasting"""

    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()

    def train_and_predict(
        self,
        historical_usage: List[int],
        forecast_periods: int = 5
    ) -> tuple[List[float], float, float]:
        """
        Train linear regression model and forecast future usage
        Returns: (predictions, trend_percentage, confidence_score)
        """

        if len(historical_usage) < 3:
            # Not enough data, return simple average
            avg = np.mean(historical_usage)
            return [avg] * forecast_periods, 0.0, 0.5

        # Prepare training data
        X = np.arange(len(historical_usage)).reshape(-1, 1)
        y = np.array(historical_usage)

        # Train model
        self.model.fit(X, y)

        # Make predictions
        future_X = np.arange(len(historical_usage), len(historical_usage) + forecast_periods).reshape(-1, 1)
        predictions = self.model.predict(future_X)

        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)

        # Calculate trend percentage
        if len(historical_usage) > 1:
            trend_slope = self.model.coef_[0]
            avg_value = np.mean(historical_usage)
            trend_percentage = (trend_slope / avg_value * 100) if avg_value > 0 else 0
        else:
            trend_percentage = 0.0

        # Calculate confidence score (R² score)
        train_predictions = self.model.predict(X)
        ss_res = np.sum((y - train_predictions) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        confidence_score = max(0, min(1, r_squared))

        return predictions.tolist(), float(trend_percentage), float(confidence_score)


class AnomalyDetectionModel:
    """Simple statistical anomaly detection for generating insights"""

    @staticmethod
    def detect_anomalies(data: List[float], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect statistical anomalies using z-score"""

        if len(data) < 3:
            return []

        data_array = np.array(data)
        mean = np.mean(data_array)
        std = np.std(data_array)

        if std == 0:
            return []

        z_scores = (data_array - mean) / std
        anomalies = []

        for i, z in enumerate(z_scores):
            if abs(z) > threshold:
                anomalies.append({
                    'index': i,
                    'value': float(data_array[i]),
                    'z_score': float(z),
                    'severity': 'high' if abs(z) > 3 else 'medium'
                })

        return anomalies


# ===========================
# BUSINESS LOGIC
# ===========================

class AnalyticsEngine:
    """Main analytics engine coordinating data generation and ML models"""

    def __init__(self):
        self.data_generator = HistoricalDataGenerator()
        self.forecast_model = InventoryForecastModel()
        self.anomaly_detector = AnomalyDetectionModel()

        # Car kit inventory configuration - 3 car types (each includes chassis + wheels + body)
        self.components_config = [
            {
                'name': 'Red Car Kit',
                'color': '#EF4444',
                'current_stock': 28,
                'base_weekly_usage': [8, 10, 9, 12, 11, 10, 9],
                'reorder_point': 15,
                'lead_time_days': 5,
                'components': {
                    'chassis': 1,
                    'wheels': 4,
                    'body': 1
                },
                'unit_cost': 45.00
            },
            {
                'name': 'Blue Car Kit',
                'color': '#3B82F6',
                'current_stock': 22,
                'base_weekly_usage': [6, 8, 7, 9, 8, 7, 8],
                'reorder_point': 12,
                'lead_time_days': 5,
                'components': {
                    'chassis': 1,
                    'wheels': 4,
                    'body': 1
                },
                'unit_cost': 45.00
            },
            {
                'name': 'Yellow Car Kit',
                'color': '#F59E0B',
                'current_stock': 18,
                'base_weekly_usage': [5, 7, 6, 8, 7, 6, 7],
                'reorder_point': 10,
                'lead_time_days': 5,
                'components': {
                    'chassis': 1,
                    'wheels': 4,
                    'body': 1
                },
                'unit_cost': 45.00
            }
        ]

    def generate_kpis(self, time_range: str = '24h') -> Dict[str, KPIData]:
        """Generate KPI data with historical trends"""

        # Determine hours based on time range
        hours_map = {'1h': 1, '24h': 24, '7d': 168, '30d': 720}
        hours = hours_map.get(time_range, 24)

        kpis = {}

        # Throughput
        throughput_history = self.data_generator.generate_kpi_history('throughput', hours)
        kpis['throughput'] = KPIData(
            current=round(throughput_history[-1], 1),
            target=300,
            trend='+12%',
            history=throughput_history
        )

        # Availability
        availability_history = self.data_generator.generate_kpi_history('availability', hours)
        kpis['availability'] = KPIData(
            current=round(availability_history[-1], 1),
            target=95,
            trend='+2.1%',
            history=availability_history
        )

        # Inventory Accuracy
        inventory_history = self.data_generator.generate_kpi_history('inventory_accuracy', hours)
        kpis['inventory_accuracy'] = KPIData(
            current=round(inventory_history[-1], 1),
            target=99,
            trend='+0.5%',
            history=inventory_history
        )

        # Cycle Time
        cycle_history = self.data_generator.generate_kpi_history('cycle_time', hours)
        kpis['cycle_time'] = KPIData(
            current=round(cycle_history[-1], 1),
            target=10,
            trend='-8%',
            history=cycle_history
        )

        # Picking Accuracy
        picking_history = self.data_generator.generate_kpi_history('picking_accuracy', hours)
        kpis['picking_accuracy'] = KPIData(
            current=round(picking_history[-1], 1),
            target=99.5,
            trend='+0.3%',
            history=picking_history
        )

        # Energy per Cycle
        energy_history = self.data_generator.generate_kpi_history('energy_per_cycle', hours)
        kpis['energy_per_cycle'] = KPIData(
            current=round(energy_history[-1], 1),
            target=2.0,
            trend='-5%',
            history=energy_history
        )

        # Error Rate
        error_history = self.data_generator.generate_kpi_history('error_rate', hours)
        kpis['error_rate'] = KPIData(
            current=round(error_history[-1], 1),
            target=2,
            trend='-15%',
            history=error_history
        )

        return kpis

    def generate_inventory_forecasts(self) -> List[ComponentForecast]:
        """Generate ML-based inventory forecasts for all car kits"""

        forecasts = []

        for component in self.components_config:
            # Add realistic variation to base usage
            weekly_usage = [
                max(1, int(val + np.random.normal(0, 1.5)))
                for val in component['base_weekly_usage']
            ]

            # Train model and predict future usage
            predictions, trend_pct, confidence = self.forecast_model.train_and_predict(
                weekly_usage,
                forecast_periods=5
            )

            # Calculate recommended order quantity
            predicted_total = sum(predictions)
            current_stock = component['current_stock']
            reorder_point = component['reorder_point']
            avg_weekly = np.mean(predictions) if predictions else np.mean(weekly_usage)

            # Calculate weeks of stock remaining
            weeks_of_stock = current_stock / avg_weekly if avg_weekly > 0 else 999

            # Determine order urgency
            if current_stock <= reorder_point:
                order_urgency = 'critical'
            elif weeks_of_stock < 3:
                order_urgency = 'soon'
            else:
                order_urgency = 'ok'

            # Calculate order by date
            lead_time = component['lead_time_days']
            days_until_reorder = max(0, (current_stock - reorder_point) / (avg_weekly / 7)) if avg_weekly > 0 else 30
            order_by = datetime.now() + timedelta(days=max(0, days_until_reorder - lead_time))

            # Order enough to cover predicted usage plus buffer
            if order_urgency == 'critical':
                recommended_order = int(predicted_total * 1.5)  # 50% safety buffer for critical
            elif order_urgency == 'soon':
                recommended_order = int(predicted_total * 1.3)  # 30% safety buffer
            else:
                recommended_order = max(0, int(predicted_total - (current_stock - reorder_point)))

            forecasts.append(ComponentForecast(
                name=component['name'],
                color=component['color'],
                current_stock=current_stock,
                weekly_usage=weekly_usage,
                predicted_usage=[round(p, 1) for p in predictions],
                recommended_order=recommended_order,
                reorder_point=reorder_point,
                lead_time_days=component['lead_time_days'],
                trend_percentage=round(trend_pct, 2),
                confidence_score=round(confidence, 2),
                components=component['components'],
                unit_cost=component['unit_cost'],
                weeks_of_stock=round(weeks_of_stock, 1),
                order_urgency=order_urgency,
                order_by_date=order_by.strftime('%b %d, %Y'),
                total_predicted_usage=round(predicted_total, 1)
            ))

        return forecasts

    def generate_ai_insights(self, kpis: Dict[str, KPIData]) -> List[AIInsight]:
        """Generate AI insights based on KPI analysis and anomaly detection"""

        insights = []

        # Analyze throughput trend
        throughput_anomalies = self.anomaly_detector.detect_anomalies(kpis['throughput'].history)
        if len(throughput_anomalies) > 0:
            insights.append(AIInsight(
                type='anomaly',
                severity='warning',
                title='Throughput Variability Detected',
                message=f'Unusual throughput patterns detected. {len(throughput_anomalies)} anomalies found in recent data. Consider investigating operational changes.',
                confidence=85,
                action='Review operational logs'
            ))

        # Check availability
        if kpis['availability'].current < kpis['availability'].target:
            insights.append(AIInsight(
                type='prediction',
                severity='warning',
                title='System Availability Below Target',
                message=f'Current availability ({kpis["availability"].current}%) is below target ({kpis["availability"].target}%). Predictive maintenance recommended.',
                confidence=92,
                action='Schedule maintenance review'
            ))

        # Energy optimization
        energy_trend = kpis['energy_per_cycle'].history
        if len(energy_trend) > 5:
            recent_avg = np.mean(energy_trend[-5:])
            overall_avg = np.mean(energy_trend)
            if recent_avg < overall_avg * 0.95:
                insights.append(AIInsight(
                    type='optimization',
                    severity='success',
                    title='Energy Efficiency Improvement',
                    message=f'Energy consumption decreased by {round((1 - recent_avg/overall_avg) * 100, 1)}% in recent periods. Recent optimizations are effective.',
                    confidence=88,
                    action='Document successful practices'
                ))

        # If no insights, add a positive one
        if len(insights) == 0:
            insights.append(AIInsight(
                type='info',
                severity='info',
                title='System Operating Normally',
                message='All KPIs are within expected ranges. System performance is stable.',
                confidence=95,
                action='Continue monitoring'
            ))

        return insights


# Initialize analytics engine
analytics_engine = AnalyticsEngine()


# ===========================
# API ENDPOINTS
# ===========================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Analytics API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(time_range: str = '24h'):
    """
    Get comprehensive analytics data including KPIs, forecasts, and AI insights

    Query Parameters:
    - time_range: Time range for historical data (1h, 24h, 7d, 30d)
    """

    try:
        # Generate KPIs with historical data
        kpis = analytics_engine.generate_kpis(time_range)

        # Generate inventory forecasts using ML
        inventory_forecasts = analytics_engine.generate_inventory_forecasts()

        # Generate AI insights
        ai_insights = analytics_engine.generate_ai_insights(kpis)

        return AnalyticsResponse(
            kpis=kpis,
            aiInsights=ai_insights,
            inventoryForecast={
                'components': inventory_forecasts
            },
            timestamp=datetime.now().isoformat(),
            model_info={
                'forecasting_model': 'Linear Regression (scikit-learn)',
                'anomaly_detection': 'Statistical Z-Score',
                'confidence_method': 'R-squared coefficient',
                'data_points_analyzed': len(kpis['throughput'].history)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")


@app.get("/api/analytics/component/{component_name}")
async def get_component_forecast(component_name: str):
    """Get detailed forecast for a specific component"""

    try:
        forecasts = analytics_engine.generate_inventory_forecasts()
        component = next((f for f in forecasts if f.name.lower() == component_name.lower()), None)

        if not component:
            raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")

        return component

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/kpis")
async def get_kpis(time_range: str = '24h'):
    """Get only KPI data"""

    try:
        kpis = analytics_engine.generate_kpis(time_range)
        return {
            'kpis': kpis,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/insights")
async def get_insights():
    """Get only AI insights"""

    try:
        kpis = analytics_engine.generate_kpis('24h')
        insights = analytics_engine.generate_ai_insights(kpis)
        return {
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)