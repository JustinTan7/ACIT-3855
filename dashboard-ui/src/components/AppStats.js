import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://sbajustin.eastus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Bullet Efficiency</th>
							<th>Ability Efficiency</th>
						</tr>
						<tr>
							<td># BE: {stats['total_bullet_efficiency_readings']}</td>
							<td># AE: {stats['total_ability_efficiency_readings']}</td>
                            <td># TR: {stats['total_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Highest gun cost: {stats['highest_gun_cost']}</td>
						</tr>
						<tr>
							<td colspan="2">Lowest gun cost: {stats['lowest_gun_cost']}</td>
						</tr>
						<tr>
							<td colspan="2">Highest round end magazine cost: {stats['highest_round_end_magazine_count']}</td>
						</tr>
                        <tr>
							<td colspan="2">Lowest round end magazine cost: {stats['lowest_round_end_magazine_count']}</td>
						</tr>
                        <tr>
							<td colspan="2">Highest ability cost: {stats['highest_ability_cost']}</td>
						</tr>
                        <tr>
							<td colspan="2">Lowest ability cost: {stats['Lowest gun cost']}</td>
						</tr>
                        <tr>
							<td colspan="2">Highest round end ability count: {stats['highest_round_end_ability_count']}</td>
						</tr>
                        <tr>
							<td colspan="2">Lowest round end ability count: {stats['lowest_round_end_ability_count']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
