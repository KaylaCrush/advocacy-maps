import React from "react"
import { Table, Container, Button } from "react-bootstrap"
import ExpandTestimony from "../ExpandTestimony/ExpandTestimony"
import { useBill, useMember } from "../db"
import { useRouter } from "next/router"
import Link from "next/link"
import { formatBillId } from "../formatting"

const MemberName = ({ memberId }) => {
  const { member, loading } = useMember(memberId)
  return <>{member?.Name}</>
}

const TestimonyRow = ({ testimony }) => {
  const { result: bill } = useBill(testimony.billId)
  const router = useRouter()

  return (
    <tr>
      <td>
        <Link href={`/bill?id=${testimony.billId}`}>
          {formatBillId(testimony.billId)}
        </Link>
      </td>
      <td>{testimony.position}</td>
      <td>
        {testimony.authorDisplayName == null ? (
          "(blank)"
        ) : (
          <Button
            variant="primary"
            onClick={() =>
              router.push(`/publicprofile?id=${testimony.authorUid}`)
            }
          >
            {testimony.authorDisplayName}
          </Button>
        )}
      </td>
      <td>{testimony.publishedAt.toDate().toLocaleString()}</td>
      <td>{testimony.content.substring(0, 100)}...</td>
      <td>
        <ExpandTestimony bill={bill?.content} testimony={testimony} />
      </td>
    </tr>
  )
}

const TestimoniesTable = ({ testimonies }) => {
  const testimoniesComponent = testimonies.map((testimony, index) => {
    return <TestimonyRow key={index} testimony={testimony} />
  })

  return (
    <Container>
      <Table responsive striped bordered hover>
        <thead>
          <tr>
            <th>Bill</th>
            <th>Position</th>
            <th>Submitter</th>
            <th>Date Submitted</th>
            <th>Text</th>
            <th></th>
          </tr>
        </thead>
        <tbody>{testimoniesComponent}</tbody>
      </Table>
    </Container>
  )
}

export default TestimoniesTable
