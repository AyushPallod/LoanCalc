import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { format, addDays, differenceInDayQs } from 'date-fns';

export default function LoanCalculator() {
  const [principal, setPrincipal] = useState('');
  const [rate, setRate] = useState('');
  const [openDate, setOpenDate] = useState('');
  const [closeDate, setCloseDate] = useState('');
  const [deposits, setDeposits] = useState([]);
  const [results, setResults] = useState([]);

  const handleDepositAdd = () => {
    setDeposits([...deposits, { date: '', amount: '' }]);
  };

  const handleDepositChange = (index, field, value) => {
    const newDeposits = [...deposits];
    newDeposits[index][field] = value;
    setDeposits(newDeposits);
  };

  const calculate = () => {
    if (!principal || !rate || !openDate) return;

    let start = new Date(openDate);
    let end = closeDate ? new Date(closeDate) : new Date();

    const totalDays = differenceInDays(end, start);
    const intervals = Math.floor(totalDays / 30);

    let p = parseFloat(principal);
    const r = parseFloat(rate) / 100 / 365; // daily rate for precise calc
    const rows = [];

    for (let i = 0; i < intervals; i++) {
      const monthStart = addDays(start, i * 30);
      const monthEnd = addDays(start, (i + 1) * 30);

      const monthDeposits = deposits.filter(dep => dep.date && new Date(dep.date) > monthStart && new Date(dep.date) <= monthEnd);

      if (monthDeposits.length === 0) {
        const interest = p * r * 30;
        p += interest;
        rows.push({ date: format(monthEnd, 'yyyy-MM-dd'), interest: interest.toFixed(2), total: p.toFixed(2) });
      } else {
        let currentPrincipal = p;
        let lastDate = monthStart;

        monthDeposits.forEach(dep => {
          const depDate = new Date(dep.date);
          const daysBefore = differenceInDays(depDate, lastDate);
          const interestBefore = currentPrincipal * r * daysBefore;
          currentPrincipal += interestBefore;
          rows.push({ date: format(depDate, 'yyyy-MM-dd'), interest: interestBefore.toFixed(2), total: currentPrincipal.toFixed(2) });

          // deposit reduces principal
          currentPrincipal -= parseFloat(dep.amount || 0);
          lastDate = depDate;
        });

        const daysAfter = differenceInDays(monthEnd, lastDate);
        const interestAfter = currentPrincipal * r * daysAfter;
        currentPrincipal += interestAfter;
        rows.push({ date: format(monthEnd, 'yyyy-MM-dd'), interest: interestAfter.toFixed(2), total: currentPrincipal.toFixed(2) });

        p = currentPrincipal;
      }
    }

    // handle remaining days if closing date is within partial month
    const lastInterestDate = addDays(start, intervals * 30);
    const remainingDays = differenceInDays(end, lastInterestDate);
    if (remainingDays > 0) {
      const interest = p * r * remainingDays;
      p += interest;
      rows.push({ date: format(end, 'yyyy-MM-dd'), interest: interest.toFixed(2), total: p.toFixed(2) });
    }

    setResults(rows);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <Card className="p-4">
        <h2 className="text-xl font-semibold mb-4">Loan Calculator</h2>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <Input placeholder="Principal Amount" type="number" value={principal} onChange={e => setPrincipal(e.target.value)} />
          <Input placeholder="Rate of Interest (annual %)" type="number" value={rate} onChange={e => setRate(e.target.value)} />
          <Input placeholder="Opening Date" type="date" value={openDate} onChange={e => setOpenDate(e.target.value)} />
          <Input placeholder="Closing Date (optional)" type="date" value={closeDate} onChange={e => setCloseDate(e.target.value)} />
        </div>

        <div className="space-y-2 mb-4">
          <h3 className="text-md font-semibold">Deposits</h3>
          {deposits.map((dep, i) => (
            <div key={i} className="grid grid-cols-2 gap-2">
              <Input type="date" value={dep.date} onChange={e => handleDepositChange(i, 'date', e.target.value)} />
              <Input type="number" placeholder="Amount" value={dep.amount} onChange={e => handleDepositChange(i, 'amount', e.target.value)} />
            </div>
          ))}
          <Button onClick={handleDepositAdd} variant="outline">Add Deposit</Button>
        </div>

        <Button onClick={calculate} className="w-full">Calculate</Button>
      </Card>

      {results.length > 0 && (
        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-2">Interest Table</h3>
          <table className="w-full border">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2">Date</th>
                <th className="border p-2">Interest</th>
                <th className="border p-2">Total Amount</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i}>
                  <td className="border p-2">{r.date}</td>
                  <td className="border p-2">{r.interest}</td>
                  <td className="border p-2">{r.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
