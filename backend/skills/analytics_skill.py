"""Analytics and reporting skill for marina management"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .base_skill import BaseSkill
from ..database.interface import DatabaseInterface
from ..utils.currency_converter import get_currency_converter
from ..logger import setup_logger


logger = setup_logger(__name__)


class AnalyticsSkill(BaseSkill):
    """Skill for analytics and reporting across all marinas"""

    def __init__(self, database: DatabaseInterface):
        super().__init__()
        self.database = database
        self.name = "analytics"
        self.description = "Generate analytics and reports for marina operations"
        self.version = "1.0.0"
        self.author = "Ada Maritime AI"
        self.currency_converter = get_currency_converter()

    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analytics operations

        Operations:
            - occupancy_report: Get occupancy statistics
            - revenue_report: Get revenue analysis
            - booking_trends: Analyze booking patterns
            - regional_overview: Get multi-region overview
            - performance_metrics: Get KPIs for marina(s)
            - customer_insights: Analyze customer behavior

        Args:
            operation: The analytics operation to perform
            parameters: Operation-specific parameters

        Returns:
            Operation results
        """
        logger.info(f"Executing analytics operation: {operation}")

        if operation == "occupancy_report":
            return await self._get_occupancy_report(parameters)
        elif operation == "revenue_report":
            return await self._get_revenue_report(parameters)
        elif operation == "booking_trends":
            return await self._get_booking_trends(parameters)
        elif operation == "regional_overview":
            return await self._get_regional_overview(parameters)
        elif operation == "performance_metrics":
            return await self._get_performance_metrics(parameters)
        elif operation == "customer_insights":
            return await self._get_customer_insights(parameters)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }

    async def _get_occupancy_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate occupancy report for marina(s)"""
        marina_id = params.get("marina_id")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        # Get marinas
        if marina_id:
            marinas = [self.database.get_marina_by_id(marina_id)]
            if not marinas[0]:
                return {"success": False, "error": f"Marina {marina_id} not found"}
        else:
            marinas = self.database.get_all_marinas()

        occupancy_data = []

        for marina in marinas:
            # Get berths for this marina
            berths = [b for b in self.database.berths if b.marina_id == marina.marina_id]

            # Calculate occupancy
            total_berths = len(berths)
            available = len([b for b in berths if b.status == "available"])
            occupied = len([b for b in berths if b.status == "occupied"])
            reserved = len([b for b in berths if b.status == "reserved"])
            maintenance = len([b for b in berths if b.status == "maintenance"])

            occupancy_rate = ((occupied + reserved) / total_berths * 100) if total_berths > 0 else 0

            occupancy_data.append({
                "marina_id": marina.marina_id,
                "marina_name": marina.name,
                "location": f"{marina.city}, {marina.country}",
                "total_berths": total_berths,
                "available": available,
                "occupied": occupied,
                "reserved": reserved,
                "maintenance": maintenance,
                "occupancy_rate": round(occupancy_rate, 2),
                "occupancy_status": self._get_occupancy_status(occupancy_rate)
            })

        # Calculate overall statistics
        total_all_berths = sum(d["total_berths"] for d in occupancy_data)
        total_occupied_reserved = sum(d["occupied"] + d["reserved"] for d in occupancy_data)
        overall_occupancy = (total_occupied_reserved / total_all_berths * 100) if total_all_berths > 0 else 0

        return {
            "success": True,
            "report_type": "occupancy",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "overall_statistics": {
                "total_marinas": len(occupancy_data),
                "total_berths": total_all_berths,
                "occupied_reserved": total_occupied_reserved,
                "overall_occupancy_rate": round(overall_occupancy, 2)
            },
            "marina_data": occupancy_data
        }

    async def _get_revenue_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate revenue report for marina(s)"""
        marina_id = params.get("marina_id")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        target_currency = params.get("currency", "EUR")

        # Get marinas
        if marina_id:
            marinas = [self.database.get_marina_by_id(marina_id)]
            if not marinas[0]:
                return {"success": False, "error": f"Marina {marina_id} not found"}
        else:
            marinas = self.database.get_all_marinas()

        revenue_data = []

        for marina in marinas:
            # Get bookings for this marina
            bookings = self.database.get_bookings_by_marina(marina.marina_id)

            # Filter by date if provided
            if start_date:
                start_dt = datetime.fromisoformat(start_date).date()
                bookings = [
                    b for b in bookings
                    if datetime.fromisoformat(b.check_in).date() >= start_dt
                ]

            if end_date:
                end_dt = datetime.fromisoformat(end_date).date()
                bookings = [
                    b for b in bookings
                    if datetime.fromisoformat(b.check_in).date() <= end_dt
                ]

            # Calculate revenue
            total_revenue = 0
            for booking in bookings:
                # Convert to target currency
                converted_amount = self.currency_converter.convert(
                    booking.total_price,
                    booking.currency,
                    target_currency
                )
                total_revenue += converted_amount

            revenue_data.append({
                "marina_id": marina.marina_id,
                "marina_name": marina.name,
                "location": f"{marina.city}, {marina.country}",
                "country": marina.country,
                "total_bookings": len(bookings),
                "total_revenue": round(total_revenue, 2),
                "currency": target_currency,
                "average_booking_value": round(total_revenue / len(bookings), 2) if bookings else 0
            })

        # Calculate totals
        total_revenue_all = sum(d["total_revenue"] for d in revenue_data)
        total_bookings_all = sum(d["total_bookings"] for d in revenue_data)

        # Sort by revenue (descending)
        revenue_data.sort(key=lambda x: x["total_revenue"], reverse=True)

        return {
            "success": True,
            "report_type": "revenue",
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "currency": target_currency,
            "overall_statistics": {
                "total_marinas": len(revenue_data),
                "total_revenue": round(total_revenue_all, 2),
                "total_bookings": total_bookings_all,
                "average_revenue_per_marina": round(total_revenue_all / len(revenue_data), 2) if revenue_data else 0
            },
            "marina_data": revenue_data
        }

    async def _get_booking_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze booking trends and patterns"""
        marina_id = params.get("marina_id")
        days_back = params.get("days_back", 90)

        # Get marinas
        if marina_id:
            marinas = [self.database.get_marina_by_id(marina_id)]
            if not marinas[0]:
                return {"success": False, "error": f"Marina {marina_id} not found"}
        else:
            marinas = self.database.get_all_marinas()

        # Collect all bookings
        all_bookings = []
        for marina in marinas:
            bookings = self.database.get_bookings_by_marina(marina.marina_id)
            all_bookings.extend(bookings)

        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_bookings = [
            b for b in all_bookings
            if datetime.fromisoformat(b.created_at) >= cutoff_date
        ]

        # Analyze trends
        bookings_by_month = defaultdict(int)
        bookings_by_day_of_week = defaultdict(int)
        avg_stay_duration = 0

        for booking in recent_bookings:
            # Month
            month = datetime.fromisoformat(booking.created_at).strftime("%Y-%m")
            bookings_by_month[month] += 1

            # Day of week
            day = datetime.fromisoformat(booking.check_in).strftime("%A")
            bookings_by_day_of_week[day] += 1

            # Duration
            avg_stay_duration += booking.total_nights

        avg_stay_duration = avg_stay_duration / len(recent_bookings) if recent_bookings else 0

        return {
            "success": True,
            "report_type": "booking_trends",
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": days_back,
            "total_bookings_analyzed": len(recent_bookings),
            "trends": {
                "bookings_by_month": dict(bookings_by_month),
                "bookings_by_day_of_week": dict(bookings_by_day_of_week),
                "average_stay_nights": round(avg_stay_duration, 1),
                "most_popular_check_in_day": max(bookings_by_day_of_week, key=bookings_by_day_of_week.get) if bookings_by_day_of_week else "N/A"
            }
        }

    async def _get_regional_overview(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive multi-region overview"""
        target_currency = params.get("currency", "EUR")

        # Get all marinas
        marinas = self.database.get_all_marinas()

        # Group by country
        by_country = defaultdict(list)
        for marina in marinas:
            by_country[marina.country].append(marina)

        regional_data = []

        for country, country_marinas in by_country.items():
            total_berths = sum(m.total_berths for m in country_marinas)
            available_berths = sum(m.available_berths for m in country_marinas)

            # Get all bookings for this country
            total_bookings = 0
            total_revenue = 0

            for marina in country_marinas:
                bookings = self.database.get_bookings_by_marina(marina.marina_id)
                total_bookings += len(bookings)

                for booking in bookings:
                    converted = self.currency_converter.convert(
                        booking.total_price,
                        booking.currency,
                        target_currency
                    )
                    total_revenue += converted

            regional_data.append({
                "country": country,
                "country_code": country_marinas[0].country_code,
                "total_marinas": len(country_marinas),
                "total_berths": total_berths,
                "available_berths": available_berths,
                "occupancy_rate": round((total_berths - available_berths) / total_berths * 100, 2) if total_berths > 0 else 0,
                "total_bookings": total_bookings,
                "total_revenue": round(total_revenue, 2),
                "currency": target_currency
            })

        # Sort by number of marinas
        regional_data.sort(key=lambda x: x["total_marinas"], reverse=True)

        return {
            "success": True,
            "report_type": "regional_overview",
            "generated_at": datetime.now().isoformat(),
            "currency": target_currency,
            "total_regions": len(regional_data),
            "total_marinas": len(marinas),
            "regions": regional_data
        }

    async def _get_performance_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get key performance indicators (KPIs)"""
        marina_id = params.get("marina_id")

        if not marina_id:
            return {"success": False, "error": "marina_id required for performance metrics"}

        marina = self.database.get_marina_by_id(marina_id)
        if not marina:
            return {"success": False, "error": f"Marina {marina_id} not found"}

        # Get berths
        berths = [b for b in self.database.berths if b.marina_id == marina_id]

        # Get bookings
        bookings = self.database.get_bookings_by_marina(marina_id)

        # Calculate KPIs
        total_berths = len(berths)
        available = len([b for b in berths if b.status == "available"])
        occupancy_rate = ((total_berths - available) / total_berths * 100) if total_berths > 0 else 0

        total_revenue = sum(b.total_price for b in bookings)
        active_bookings = len([b for b in bookings if b.is_active])

        # Average daily rate
        total_nights = sum(b.total_nights for b in bookings)
        avg_daily_rate = (total_revenue / total_nights) if total_nights > 0 else 0

        # Revenue per available berth
        rev_par = (total_revenue / total_berths) if total_berths > 0 else 0

        return {
            "success": True,
            "marina_id": marina_id,
            "marina_name": marina.name,
            "generated_at": datetime.now().isoformat(),
            "kpis": {
                "occupancy_rate": round(occupancy_rate, 2),
                "total_berths": total_berths,
                "available_berths": available,
                "total_bookings": len(bookings),
                "active_bookings": active_bookings,
                "total_revenue": round(total_revenue, 2),
                "currency": marina.currency,
                "average_daily_rate": round(avg_daily_rate, 2),
                "revenue_per_available_berth": round(rev_par, 2),
                "average_length_of_stay": round(sum(b.total_nights for b in bookings) / len(bookings), 1) if bookings else 0
            },
            "performance_rating": self._calculate_performance_rating(occupancy_rate, rev_par)
        }

    async def _get_customer_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer behavior and patterns"""
        marina_id = params.get("marina_id")

        # Get bookings
        if marina_id:
            bookings = self.database.get_bookings_by_marina(marina_id)
        else:
            all_bookings = []
            for marina in self.database.get_all_marinas():
                all_bookings.extend(self.database.get_bookings_by_marina(marina.marina_id))
            bookings = all_bookings

        if not bookings:
            return {
                "success": True,
                "message": "No bookings found for analysis"
            }

        # Analyze customer patterns
        boat_lengths = [b.boat_length_meters for b in bookings]
        avg_boat_length = sum(boat_lengths) / len(boat_lengths)

        # Most requested services
        service_counts = defaultdict(int)
        for booking in bookings:
            for service in booking.services_requested:
                service_counts[service] += 1

        top_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "success": True,
            "report_type": "customer_insights",
            "generated_at": datetime.now().isoformat(),
            "total_customers_analyzed": len(bookings),
            "insights": {
                "average_boat_length_meters": round(avg_boat_length, 1),
                "min_boat_length": min(boat_lengths),
                "max_boat_length": max(boat_lengths),
                "top_requested_services": [
                    {"service": service, "count": count}
                    for service, count in top_services
                ]
            }
        }

    def _get_occupancy_status(self, rate: float) -> str:
        """Get status description for occupancy rate"""
        if rate >= 90:
            return "Excellent"
        elif rate >= 75:
            return "Good"
        elif rate >= 50:
            return "Moderate"
        else:
            return "Low"

    def _calculate_performance_rating(self, occupancy: float, rev_par: float) -> str:
        """Calculate overall performance rating"""
        score = (occupancy / 100) * 0.6 + (min(rev_par / 1000, 1)) * 0.4

        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
